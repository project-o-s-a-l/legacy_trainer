from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

import backend.models  # noqa: F401
from backend.app.db.base import Base
from backend.app.db.enums import TaskDifficulty, TaskStatus, UserRole
from backend.app.db.session import SessionLocal, engine
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task
from backend.app.models.task_check_rule import TaskCheckRule
from backend.app.models.task_scenario import TaskScenario
from backend.app.models.user import User
from backend.app.services.security import hash_password


SEED_AUTHOR_EMAIL = "seed.author@example.com"
SEED_AUTHOR_USERNAME = "seed_author"
SEED_AUTHOR_PASSWORD = "seed_author_password"


def ensure_author(db: Session) -> User:
    stmt = select(User).where(
        or_(
            User.email == SEED_AUTHOR_EMAIL,
            User.username == SEED_AUTHOR_USERNAME,
            User.login == SEED_AUTHOR_USERNAME,
        )
    )
    user = db.scalar(stmt)
    if user is not None:
        user.email = SEED_AUTHOR_EMAIL
        user.username = SEED_AUTHOR_USERNAME
        user.login = SEED_AUTHOR_USERNAME
        user.password_hash = hash_password(SEED_AUTHOR_PASSWORD)
        user.role = UserRole.ADMIN
        user.email_verified_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        return user

    user = User(
        username=SEED_AUTHOR_USERNAME,
        email=SEED_AUTHOR_EMAIL,
        login=SEED_AUTHOR_USERNAME,
        password_hash=hash_password(SEED_AUTHOR_PASSWORD),
        role=UserRole.ADMIN,
        email_verified_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def ensure_language(
    db: Session,
    *,
    name: str,
    display_name: str,
    version: str,
) -> ProgramLanguage:
    stmt = select(ProgramLanguage).where(ProgramLanguage.name == name)
    language = db.scalar(stmt)
    if language is None:
        language = ProgramLanguage(
            name=name,
            display_name=display_name,
            version=version,
        )
        db.add(language)
        db.flush()
        db.refresh(language)
        return language

    language.display_name = display_name
    language.version = version
    return language


def ensure_task(
    db: Session,
    *,
    author: User,
    language: ProgramLanguage,
    title: str,
    description: str,
    requirements: str,
    legacy_code: str,
    difficulty: TaskDifficulty,
    max_score: int,
) -> Task:
    stmt = select(Task).where(Task.title == title)
    task = db.scalar(stmt)
    if task is None:
        task = Task(
            title=title,
            description=description,
            requirements=requirements,
            legacy_code=legacy_code,
            difficulty=difficulty,
            author_id=author.id,
            status=TaskStatus.PUBLISHED,
            max_score=max_score,
        )
        task.languages.append(language)
        db.add(task)
        db.flush()
        db.refresh(task)
        return task

    task.description = description
    task.requirements = requirements
    task.legacy_code = legacy_code
    task.difficulty = difficulty
    task.author_id = author.id
    task.status = TaskStatus.PUBLISHED
    task.max_score = max_score
    if all(item.id != language.id for item in task.languages):
        task.languages.append(language)
    return task


def replace_task_configuration(
    db: Session,
    *,
    task: Task,
    language_name: str,
    scenarios: list[dict],
    rules: list[dict],
) -> None:
    existing_scenarios = [
        item for item in task.scenarios if item.language_name == language_name
    ]
    for item in existing_scenarios:
        db.delete(item)

    existing_rules = [
        item for item in task.check_rules if item.language_name == language_name
    ]
    for item in existing_rules:
        db.delete(item)
    db.flush()

    for index, scenario in enumerate(scenarios, start=1):
        db.add(
            TaskScenario(
                task_id=task.id,
                language_name=language_name,
                name=scenario["name"],
                order_index=index,
                weight=scenario.get("weight", 1),
                input_payload=scenario["input_payload"],
                expected_output=scenario.get("expected_output"),
            )
        )

    for rule in rules:
        db.add(
            TaskCheckRule(
                task_id=task.id,
                language_name=language_name,
                rule_type=rule["rule_type"],
                weight=rule["weight"],
                config_json=rule["config_json"],
            )
        )


def seed_python_task(db: Session, *, author: User, language: ProgramLanguage) -> Task:
    task = ensure_task(
        db,
        author=author,
        language=language,
        title="Python: Refactor Order Formatter",
        description=(
            "Пользователь получает процедурный модуль, который считает итоговую сумму "
            "заказа и формирует словарь результата. Нужно провести рефакторинг без "
            "изменения поведения."
        ),
        requirements=(
            "Сохрани поведение функции format_order(total, vip=False), "
            "вынеси расчёт скидки в отдельную функцию apply_discount, "
            "не добавляй глобальное состояние и не оставляй TODO/pass."
        ),
        legacy_code=(
            "def format_order(total, vip=False):\n"
            "    discount = 0.1 if vip else 0.0\n"
            "    final_total = round(total * (1 - discount), 2)\n"
            "    return {'final_total': final_total, 'vip': vip}\n"
        ),
        difficulty=TaskDifficulty.EASY,
        max_score=100,
    )

    replace_task_configuration(
        db,
        task=task,
        language_name="python",
        scenarios=[
            {
                "name": "vip-order",
                "input_payload": {"args": [100, True], "kwargs": {}},
            },
            {
                "name": "regular-order",
                "input_payload": {"args": [80, False], "kwargs": {}},
            },
            {
                "name": "fractional-order",
                "input_payload": {"args": [19.99, True], "kwargs": {}},
            },
        ],
        rules=[
            {
                "rule_type": "behavior",
                "weight": 70,
                "config_json": {
                    "mode": "python_function",
                    "entrypoint": "format_order",
                },
            },
            {
                "rule_type": "contract",
                "weight": 10,
                "config_json": {
                    "required_functions": ["format_order", "apply_discount"],
                },
            },
            {
                "rule_type": "structure",
                "weight": 10,
                "config_json": {
                    "required_tokens": ["apply_discount"],
                    "forbid_global_assignments": True,
                    "max_top_level_statements": 0,
                    "max_function_length": 12,
                },
            },
            {
                "rule_type": "quality",
                "weight": 10,
                "config_json": {
                    "forbidden_markers": ["TODO", "pass", "NotImplementedError"],
                    "max_lines": 40,
                },
            },
        ],
    )
    return task


def seed_cpp_task(db: Session, *, author: User, language: ProgramLanguage) -> Task:
    task = ensure_task(
        db,
        author=author,
        language=language,
        title="C++: Refactor Number Doubler",
        description=(
            "Пользователь получает одномодульную C++-программу, которая читает число "
            "из stdin и печатает удвоенное значение. Нужно провести рефакторинг без "
            "изменения поведения."
        ),
        requirements=(
            "Сохрани то же поведение на stdin/stdout, добавь класс или struct для "
            "основной логики и не теряй поддержку текущего формата ввода."
            "Важно: отдельного поля для ручного ввода stdin в интерфейсе нет. "
            "Во время проверки тестовые входные данные подаются системой автоматически."
        ),
        legacy_code=(
            "#include <iostream>\n"
            "int main() {\n"
            "    long long value = 0;\n"
            "    if (!(std::cin >> value)) {\n"
            "        return 0;\n"
            "    }\n"
            "    std::cout << value * 2 << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        difficulty=TaskDifficulty.EASY,
        max_score=100,
    )

    replace_task_configuration(
        db,
        task=task,
        language_name="cpp",
        scenarios=[
            {
                "name": "double-3",
                "input_payload": {"stdin": "3\n"},
            },
            {
                "name": "double-7",
                "input_payload": {"stdin": "7\n"},
            },
            {
                "name": "double-0",
                "input_payload": {"stdin": "0\n"},
            },
        ],
        rules=[
            {
                "rule_type": "behavior",
                "weight": 80,
                "config_json": {"mode": "stdin"},
            },
            {
                "rule_type": "contract",
                "weight": 10,
                "config_json": {"required_tokens": ["Doubler"]},
            },
            {
                "rule_type": "structure",
                "weight": 10,
                "config_json": {
                    "minimum_class_count": 1,
                    "required_tokens": ["Doubler"],
                },
            },
        ],
    )
    return task


def seed_python_medium_task(
    db: Session,
    *,
    author: User,
    language: ProgramLanguage,
) -> Task:
    task = ensure_task(
        db,
        author=author,
        language=language,
        title="Python Medium: Refactor User Payload Validator",
        description=(
            "Пользователь получает легаси-модуль для валидации профиля пользователя. "
            "Нужно сохранить поведение и вынести нормализацию/валидацию в более "
            "читаемую структуру."
        ),
        requirements=(
            "Сохрани поведение функции validate_user_payload(payload), "
            "добавь вспомогательную функцию normalize_name и не используй "
            "глобальное состояние."
        ),
        legacy_code=(
            "def validate_user_payload(payload):\n"
            "    name = str(payload.get('name', '')).strip()\n"
            "    age = payload.get('age')\n"
            "    is_active = bool(payload.get('is_active', False))\n"
            "    valid = bool(name) and isinstance(age, int) and age >= 18\n"
            "    return {\n"
            "        'name': name.title(),\n"
            "        'age': age,\n"
            "        'is_active': is_active,\n"
            "        'is_valid': valid,\n"
            "    }\n"
        ),
        difficulty=TaskDifficulty.MEDIUM,
        max_score=100,
    )

    replace_task_configuration(
        db,
        task=task,
        language_name="python",
        scenarios=[
            {
                "name": "adult-active-user",
                "input_payload": {
                    "args": [{"name": "  alice  ", "age": 24, "is_active": 1}],
                    "kwargs": {},
                },
            },
            {
                "name": "underage-user",
                "input_payload": {
                    "args": [{"name": "bob", "age": 15, "is_active": 0}],
                    "kwargs": {},
                },
            },
            {
                "name": "missing-name",
                "input_payload": {
                    "args": [{"name": "   ", "age": 34, "is_active": True}],
                    "kwargs": {},
                },
            },
        ],
        rules=[
            {
                "rule_type": "behavior",
                "weight": 65,
                "config_json": {
                    "mode": "python_function",
                    "entrypoint": "validate_user_payload",
                },
            },
            {
                "rule_type": "contract",
                "weight": 15,
                "config_json": {
                    "required_functions": [
                        "validate_user_payload",
                        "normalize_name",
                    ],
                },
            },
            {
                "rule_type": "structure",
                "weight": 10,
                "config_json": {
                    "required_tokens": ["normalize_name"],
                    "forbid_global_assignments": True,
                    "max_top_level_statements": 0,
                    "max_function_length": 18,
                },
            },
            {
                "rule_type": "quality",
                "weight": 10,
                "config_json": {
                    "forbidden_markers": ["TODO", "pass", "NotImplementedError"],
                    "max_lines": 60,
                },
            },
        ],
    )
    return task


def seed_cpp_medium_task(
    db: Session,
    *,
    author: User,
    language: ProgramLanguage,
) -> Task:
    task = ensure_task(
        db,
        author=author,
        language=language,
        title="C++ Medium: Refactor Line Normalizer",
        description=(
            "Пользователь получает одномодульную программу, которая читает строку и "
            "нормализует множественные пробелы. Нужно сохранить поведение и "
            "переложить логику в отдельную структуру."
        ),
        requirements=(
            "Сохрани поведение на stdin/stdout, выдели основную логику в класс или "
            "struct Normalizer и не ломай обработку пустого ввода."
            "Важно: отдельного поля для ручного ввода stdin в интерфейсе нет. "
            "Во время проверки тестовые входные данные подаются системой автоматически."
        ),
        legacy_code=(
            "#include <iostream>\n"
            "#include <sstream>\n"
            "#include <string>\n"
            "int main() {\n"
            "    std::string line;\n"
            "    std::getline(std::cin, line);\n"
            "    std::stringstream input(line);\n"
            "    std::string word;\n"
            "    bool first = true;\n"
            "    while (input >> word) {\n"
            "        if (!first) {\n"
            "            std::cout << ' ';\n"
            "        }\n"
            "        std::cout << word;\n"
            "        first = false;\n"
            "    }\n"
            "    std::cout << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        difficulty=TaskDifficulty.MEDIUM,
        max_score=100,
    )

    replace_task_configuration(
        db,
        task=task,
        language_name="cpp",
        scenarios=[
            {
                "name": "extra-spaces",
                "input_payload": {"stdin": "  hello   world  \n"},
            },
            {
                "name": "single-word",
                "input_payload": {"stdin": "legacy\n"},
            },
            {
                "name": "empty-line",
                "input_payload": {"stdin": "\n"},
            },
        ],
        rules=[
            {
                "rule_type": "behavior",
                "weight": 75,
                "config_json": {"mode": "stdin"},
            },
            {
                "rule_type": "contract",
                "weight": 10,
                "config_json": {"required_tokens": ["Normalizer"]},
            },
            {
                "rule_type": "structure",
                "weight": 15,
                "config_json": {
                    "minimum_class_count": 1,
                    "required_tokens": ["Normalizer"],
                },
            },
        ],
    )
    return task


def seed_python_hard_task(
    db: Session,
    *,
    author: User,
    language: ProgramLanguage,
) -> Task:
    task = ensure_task(
        db,
        author=author,
        language=language,
        title="Python Hard: Refactor Transaction Aggregator",
        description=(
            "Пользователь получает легаси-модуль, который агрегирует список "
            "транзакций по доходам, расходам и балансу. Нужно сохранить поведение и "
            "сделать модуль менее хрупким."
        ),
        requirements=(
            "Сохрани поведение функции aggregate_transactions(items), "
            "выдели функцию normalize_amount и не оставляй procedural-мусор в "
            "глобальной области."
        ),
        legacy_code=(
            "def aggregate_transactions(items):\n"
            "    income = 0.0\n"
            "    expense = 0.0\n"
            "    for item in items:\n"
            "        amount = float(item.get('amount', 0))\n"
            "        if item.get('type') == 'income':\n"
            "            income += amount\n"
            "        else:\n"
            "            expense += amount\n"
            "    income = round(income, 2)\n"
            "    expense = round(expense, 2)\n"
            "    return {\n"
            "        'income': income,\n"
            "        'expense': expense,\n"
            "        'balance': round(income - expense, 2),\n"
            "        'count': len(items),\n"
            "    }\n"
        ),
        difficulty=TaskDifficulty.HARD,
        max_score=100,
    )

    replace_task_configuration(
        db,
        task=task,
        language_name="python",
        scenarios=[
            {
                "name": "mixed-transactions",
                "input_payload": {
                    "args": [[
                        {"type": "income", "amount": "100.50"},
                        {"type": "expense", "amount": "25.10"},
                        {"type": "income", "amount": 10},
                    ]],
                    "kwargs": {},
                },
            },
            {
                "name": "only-expenses",
                "input_payload": {
                    "args": [[
                        {"type": "expense", "amount": 15},
                        {"type": "expense", "amount": "5.75"},
                    ]],
                    "kwargs": {},
                },
            },
            {
                "name": "empty-list",
                "input_payload": {"args": [[]], "kwargs": {}},
            },
        ],
        rules=[
            {
                "rule_type": "behavior",
                "weight": 65,
                "config_json": {
                    "mode": "python_function",
                    "entrypoint": "aggregate_transactions",
                },
            },
            {
                "rule_type": "contract",
                "weight": 15,
                "config_json": {
                    "required_functions": [
                        "aggregate_transactions",
                        "normalize_amount",
                    ],
                },
            },
            {
                "rule_type": "structure",
                "weight": 10,
                "config_json": {
                    "required_tokens": ["normalize_amount"],
                    "forbid_global_assignments": True,
                    "max_top_level_statements": 0,
                    "max_function_length": 20,
                },
            },
            {
                "rule_type": "quality",
                "weight": 10,
                "config_json": {
                    "forbidden_markers": ["TODO", "pass", "NotImplementedError"],
                    "max_lines": 70,
                },
            },
        ],
    )
    return task


def seed_cpp_hard_task(
    db: Session,
    *,
    author: User,
    language: ProgramLanguage,
) -> Task:
    task = ensure_task(
        db,
        author=author,
        language=language,
        title="C++ Hard: Refactor Metrics Transformer",
        description=(
            "Пользователь получает одномодульную программу, которая читает набор "
            "целых чисел и выводит сумму, минимум и максимум. Нужно провести "
            "рефакторинг без изменения поведения."
        ),
        requirements=(
            "Сохрани поведение на stdin/stdout, выдели отдельную структуру "
            "MetricsCalculator и сохрани корректную обработку пустого ввода."
            "Важно: отдельного поля для ручного ввода stdin в интерфейсе нет. "
            "Во время проверки тестовые входные данные подаются системой автоматически."
        ),
        legacy_code=(
            "#include <iostream>\n"
            "#include <limits>\n"
            "int main() {\n"
            "    long long value = 0;\n"
            "    long long sum = 0;\n"
            "    long long min_value = std::numeric_limits<long long>::max();\n"
            "    long long max_value = std::numeric_limits<long long>::min();\n"
            "    int count = 0;\n"
            "    while (std::cin >> value) {\n"
            "        sum += value;\n"
            "        if (value < min_value) min_value = value;\n"
            "        if (value > max_value) max_value = value;\n"
            "        ++count;\n"
            "    }\n"
            "    if (count == 0) {\n"
            "        std::cout << \"0 0 0\" << std::endl;\n"
            "        return 0;\n"
            "    }\n"
            "    std::cout << sum << ' ' << min_value << ' ' << max_value << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        difficulty=TaskDifficulty.HARD,
        max_score=100,
    )

    replace_task_configuration(
        db,
        task=task,
        language_name="cpp",
        scenarios=[
            {
                "name": "positive-values",
                "input_payload": {"stdin": "1 5 3\n"},
            },
            {
                "name": "mixed-values",
                "input_payload": {"stdin": "-2 7 4 -1\n"},
            },
            {
                "name": "empty-input",
                "input_payload": {"stdin": ""},
            },
        ],
        rules=[
            {
                "rule_type": "behavior",
                "weight": 75,
                "config_json": {"mode": "stdin"},
            },
            {
                "rule_type": "contract",
                "weight": 10,
                "config_json": {"required_tokens": ["MetricsCalculator"]},
            },
            {
                "rule_type": "structure",
                "weight": 15,
                "config_json": {
                    "minimum_class_count": 1,
                    "required_tokens": ["MetricsCalculator"],
                },
            },
        ],
    )
    return task


def main() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        author = ensure_author(db)
        python_language = ensure_language(
            db,
            name="python",
            display_name="Python",
            version="3.12",
        )
        cpp_language = ensure_language(
            db,
            name="cpp",
            display_name="C++",
            version="17",
        )

        python_task = seed_python_task(db, author=author, language=python_language)
        cpp_task = seed_cpp_task(db, author=author, language=cpp_language)
        python_medium_task = seed_python_medium_task(
            db,
            author=author,
            language=python_language,
        )
        cpp_medium_task = seed_cpp_medium_task(
            db,
            author=author,
            language=cpp_language,
        )
        python_hard_task = seed_python_hard_task(
            db,
            author=author,
            language=python_language,
        )
        cpp_hard_task = seed_cpp_hard_task(
            db,
            author=author,
            language=cpp_language,
        )

        db.commit()

        print("Seed completed successfully")
        print(f"Author login: {author.login}")
        print(f"Python task id: {python_task.id}")
        print(f"C++ task id: {cpp_task.id}")
        print(f"Python medium task id: {python_medium_task.id}")
        print(f"C++ medium task id: {cpp_medium_task.id}")
        print(f"Python hard task id: {python_hard_task.id}")
        print(f"C++ hard task id: {cpp_hard_task.id}")


if __name__ == "__main__":
    main()
