import shutil

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.db.enums import TaskDifficulty, TaskStatus, UserRole
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.task import Task
from backend.app.models.task_check_rule import TaskCheckRule
from backend.app.models.task_scenario import TaskScenario
from backend.app.models.user import User
from backend.app.services.security import hash_password
from backend.app.services.token import create_access_token


def create_user(
    db_session: Session,
    *,
    username: str = "refactor-user",
    email: str = "refactor-user@example.com",
    login: str = "refactor-user",
    password: str = "password123",
) -> User:
    user = User(
        username=username,
        email=email,
        login=login,
        password_hash=hash_password(password),
        role=UserRole.USER,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


def authenticate_client(client: TestClient, user: User) -> None:
    token = create_access_token(user.id)
    client.cookies.set("access_token", token)


def create_language(
    db_session: Session,
    *,
    name: str,
    display_name: str,
    version: str,
) -> ProgramLanguage:
    language = ProgramLanguage(
        name=name,
        display_name=display_name,
        version=version,
    )
    db_session.add(language)
    db_session.flush()
    db_session.refresh(language)
    return language


def create_task(
    db_session: Session,
    *,
    author: User,
    language: ProgramLanguage,
    title: str,
    legacy_code: str,
    difficulty: TaskDifficulty = TaskDifficulty.EASY,
    status: TaskStatus = TaskStatus.PUBLISHED,
    max_score: int = 100,
) -> Task:
    task = Task(
        title=title,
        description=f"{title} description",
        requirements=f"{title} requirements",
        legacy_code=legacy_code,
        difficulty=difficulty,
        author_id=author.id,
        status=status,
        max_score=max_score,
        languages=[language],
    )
    db_session.add(task)
    db_session.flush()
    db_session.refresh(task)
    return task


def create_scenario(
    db_session: Session,
    *,
    task: Task,
    language_name: str,
    name: str,
    input_payload: dict,
    expected_output=None,
    order_index: int = 0,
    weight: int = 1,
) -> TaskScenario:
    scenario = TaskScenario(
        task_id=task.id,
        language_name=language_name,
        name=name,
        input_payload=input_payload,
        expected_output=expected_output,
        order_index=order_index,
        weight=weight,
    )
    db_session.add(scenario)
    db_session.flush()
    db_session.refresh(scenario)
    return scenario


def create_rule(
    db_session: Session,
    *,
    task: Task,
    language_name: str,
    rule_type: str,
    weight: int,
    config_json: dict,
) -> TaskCheckRule:
    rule = TaskCheckRule(
        task_id=task.id,
        language_name=language_name,
        rule_type=rule_type,
        weight=weight,
        config_json=config_json,
    )
    db_session.add(rule)
    db_session.flush()
    db_session.refresh(rule)
    return rule


def test_submit_solution_runs_python_refactor_checks_from_db(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    python_language = create_language(
        db_session,
        name="python",
        display_name="Python",
        version="3.12",
    )
    task = create_task(
        db_session,
        author=user,
        language=python_language,
        title="Python refactor task",
        legacy_code=(
            "def format_order(total, vip=False):\n"
            "    discount = 0.1 if vip else 0.0\n"
            "    final_total = round(total * (1 - discount), 2)\n"
            "    return {'final_total': final_total, 'vip': vip}\n"
        ),
    )
    create_scenario(
        db_session,
        task=task,
        language_name="python",
        name="vip-order",
        input_payload={"args": [100, True], "kwargs": {}},
        order_index=1,
    )
    create_scenario(
        db_session,
        task=task,
        language_name="python",
        name="regular-order",
        input_payload={"args": [80, False], "kwargs": {}},
        order_index=2,
    )
    create_rule(
        db_session,
        task=task,
        language_name="python",
        rule_type="behavior",
        weight=70,
        config_json={"mode": "python_function", "entrypoint": "format_order"},
    )
    create_rule(
        db_session,
        task=task,
        language_name="python",
        rule_type="contract",
        weight=10,
        config_json={"required_functions": ["format_order", "apply_discount"]},
    )
    create_rule(
        db_session,
        task=task,
        language_name="python",
        rule_type="structure",
        weight=10,
        config_json={
            "required_tokens": ["apply_discount"],
            "forbid_global_assignments": True,
            "max_top_level_statements": 0,
        },
    )
    create_rule(
        db_session,
        task=task,
        language_name="python",
        rule_type="quality",
        weight=10,
        config_json={"forbidden_markers": ["TODO", "pass", "NotImplementedError"]},
    )
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": (
                "def apply_discount(total, vip=False):\n"
                "    return round(total * (0.9 if vip else 1.0), 2)\n\n"
                "def format_order(total, vip=False):\n"
                "    return {\n"
                "        'final_total': apply_discount(total, vip),\n"
                "        'vip': vip,\n"
                "    }\n"
            ),
            "language": "python",
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["status"] == "passed"
    assert body["score"] == 100
    assert body["message"] == "Behaviour preserved for 2 of 2 scenarios"
    assert body["testPassed"] == 2

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    checks = checks_response.json()

    assert len(checks) == 4
    assert checks[0]["checkType"] == "tests"
    assert checks[0]["status"] == "passed"
    assert checks[0]["report"]["passed"] == 2
    assert checks[1]["checkType"] == "static"
    assert checks[1]["status"] == "passed"
    assert checks[2]["checkType"] == "architecture"
    assert checks[2]["status"] == "passed"
    assert checks[3]["checkType"] == "lint"
    assert checks[3]["status"] == "passed"


@pytest.mark.skipif(shutil.which("g++") is None, reason="g++ is not installed")
def test_submit_solution_runs_cpp_refactor_checks_from_db(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="cpp-refactor-user",
        email="cpp-refactor-user@example.com",
        login="cpp-refactor-user",
    )
    cpp_language = create_language(
        db_session,
        name="cpp",
        display_name="C++",
        version="17",
    )
    task = create_task(
        db_session,
        author=user,
        language=cpp_language,
        title="Cpp refactor task",
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
    )
    create_scenario(
        db_session,
        task=task,
        language_name="cpp",
        name="double-3",
        input_payload={"stdin": "3\n"},
        order_index=1,
    )
    create_scenario(
        db_session,
        task=task,
        language_name="cpp",
        name="double-7",
        input_payload={"stdin": "7\n"},
        order_index=2,
    )
    create_rule(
        db_session,
        task=task,
        language_name="cpp",
        rule_type="behavior",
        weight=80,
        config_json={"mode": "stdin"},
    )
    create_rule(
        db_session,
        task=task,
        language_name="cpp",
        rule_type="contract",
        weight=10,
        config_json={"required_tokens": ["Doubler"]},
    )
    create_rule(
        db_session,
        task=task,
        language_name="cpp",
        rule_type="structure",
        weight=10,
        config_json={"minimum_class_count": 1},
    )
    db_session.commit()

    authenticate_client(client, user)

    response = client.post(
        f"/api/v1/tasks/{task.id}/submit",
        json={
            "code": (
                "#include <iostream>\n"
                "class Doubler {\n"
                "public:\n"
                "    static long long run(long long value) {\n"
                "        return value * 2;\n"
                "    }\n"
                "};\n"
                "int main() {\n"
                "    long long value = 0;\n"
                "    if (!(std::cin >> value)) {\n"
                "        return 0;\n"
                "    }\n"
                "    std::cout << Doubler::run(value) << std::endl;\n"
                "    return 0;\n"
                "}\n"
            ),
            "language": "cpp",
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["status"] == "passed"
    assert body["score"] == 100
    assert body["message"] == "Behaviour preserved for 2 of 2 scenarios"
    assert body["testPassed"] == 2

    checks_response = client.get(f"/api/v1/submissions/{body['submissionId']}/checks")
    assert checks_response.status_code == 200
    checks = checks_response.json()

    assert len(checks) == 3
    assert checks[0]["checkType"] == "tests"
    assert checks[0]["status"] == "passed"
    assert checks[0]["report"]["passed"] == 2
    assert checks[1]["checkType"] == "static"
    assert checks[1]["status"] == "passed"
    assert checks[2]["checkType"] == "architecture"
    assert checks[2]["status"] == "passed"
