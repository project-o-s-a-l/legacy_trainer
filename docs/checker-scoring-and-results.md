# Code Checker Scoring and Result Evaluation

Этот документ описывает, как backend оценивает отправленное решение, из чего
складывается итоговый результат и какие настройки задачи влияют на статус,
баллы, прогресс пользователя и отображаемые детали проверки.

## Краткая схема

Когда пользователь отправляет решение через `POST /api/v1/tasks/{task_id}/submit`,
backend:

1. Проверяет, что задача существует.
2. Проверяет, что код не пустой.
3. Нормализует язык решения (`python`, `cpp`, `c++`).
4. Проверяет, что выбранный язык доступен для задачи.
5. Создает запись `Submission` со статусом `pending`.
6. Запускает подходящую систему проверок.
7. Записывает итоговые поля `Submission`.
8. Сохраняет все отдельные `SubmissionCheck`.
9. Обновляет `UserTaskProgress` и `User.total_score`.
10. Возвращает краткий результат проверки.

Итоговая запись `Submission` получает:

- `status` - общий статус проверки: `passed`, `failed`, `error`.
- `score` - итоговый балл.
- `checked_at` - время завершения проверки.
- `memory_used_kb` - агрегированная память.
- `execution_time_ms` - агрегированное время выполнения.

Каждая отдельная проверка сохраняется как `SubmissionCheck`:

- `check_type` - тип проверки: `tests`, `lint`, `static`, `architecture`.
- `status` - статус конкретной проверки.
- `score` - балл конкретной проверки от `0` до `100`.
- `report_json` - подробный отчет.

## Какие системы проверки могут запускаться

Backend выбирает один путь проверки для каждой отправки.

### 1. Новая система `TaskCheckSpec`

Если у задачи есть `task.check_specs`, используется новый orchestrator:

```text
TaskCheckSpec -> CheckOrchestrator -> runner -> CheckRunResult
```

Поддерживаемые типы проверок:

- `tests` - запуск pytest внутри sandbox container.
- `lint` - запуск Ruff внутри sandbox container.
- `static` - AST-проверки Python-кода.
- `architecture` - AST-проверки архитектурных правил.

Это основной формат для новых задач.

### 2. Legacy refactor pipeline

Если `TaskCheckSpec` у задачи нет, backend пробует старую систему:

```text
TaskScenario / TaskCheckRule -> RefactorCheckPipeline
```

Она нужна для существующих refactor-задач и поддерживает текущие Python/C++
проверки рефакторинга.

### 3. Deterministic fallback

Если у задачи нет ни `TaskCheckSpec`, ни legacy refactor-настроек, используется
детерминированный fallback для базовой проверки. Это запасной путь, а не
рекомендуемый формат для новых задач.

## Основные поля `TaskCheckSpec`

На результат новой системы больше всего влияют поля check spec:

- `check_type` - какой runner будет запущен.
- `name` - человекочитаемое имя проверки.
- `weight` - вес проверки в итоговом score.
- `is_required` - влияет ли провал проверки на общий `Submission.status`.
- `timeout_seconds` - лимит времени конкретной проверки.
- `order` - порядок запуска и отображения проверок.
- `config_json` - настройки конкретного runner.

Проверки выполняются в порядке:

```text
(order, id)
```

## Итоговый score в новой системе

Каждая проверка возвращает собственный `score` от `0` до `100`.

Итоговый score считается как взвешенное среднее по проверкам с положительным
весом:

```text
int(sum(check.score * check.weight) / sum(check.weight))
```

Проверки с `weight <= 0` не участвуют в расчете итогового score.

Примеры:

```text
tests:  score=100, weight=75
lint:   score=0,   weight=25
result: int((100 * 75 + 0 * 25) / 100) = 75
```

```text
tests:        score=50,  weight=80
architecture: score=100, weight=20
result: int((50 * 80 + 100 * 20) / 100) = 60
```

Если ни одна проверка не имеет положительного веса, итоговый score будет `0`.

## Итоговый status в новой системе

Итоговый `Submission.status` считается отдельно от score.

Правила:

1. Если любая обязательная проверка (`is_required=True`) завершилась со
   статусом `error`, итоговый статус будет `error`.
2. Иначе, если любая обязательная проверка завершилась со статусом `failed`,
   итоговый статус будет `failed`.
3. Иначе итоговый статус будет `passed`.

Важно: необязательная проверка (`is_required=False`) может уменьшить итоговый
score, но сама по себе не делает submission failed.

Пример:

```text
tests: required, passed, score=100, weight=75
lint: optional, failed, score=0, weight=25

Submission.status = passed
Submission.score = 75
```

Пример с обязательной проверкой:

```text
tests: required, failed, score=50, weight=100

Submission.status = failed
Submission.score = 50
```

То есть failed submission может сохранить частичные баллы. Это ожидаемое
поведение текущей системы.

## Что означает `error`

`error` означает, что проверка не смогла корректно выполниться или корректно
вернуть результат.

Причины могут быть такими:

- неверный `config_json`;
- неподдерживаемый язык для runner;
- syntax error;
- timeout;
- ошибка sandbox container;
- sandbox вернул невалидный JSON;
- sandbox вернул отчет неправильной структуры;
- отсутствует runner для указанного `check_type`.

Обычно `error` дает score `0` для конкретной проверки.

Если `error` случился в обязательной проверке, весь submission получает
`status=error`.

## Как работают отдельные типы проверок

### `tests`

Runner запускает pytest внутри sandbox container.

Настройки в `config_json`:

```json
{
  "entry_file": "solution.py",
  "test_file": "test_solution.py",
  "test_code": "...",
  "visible": false
}
```

Что влияет на результат:

- сколько pytest-тестов прошло;
- сколько тестов упало;
- были ли ошибки выполнения;
- был ли timeout;
- корректно ли сформирован `config_json`;
- уложился ли runner в `timeout_seconds`.

Score:

```text
int((passed / total) * 100)
```

Если все тесты прошли, check получает:

```text
status = passed
score = 100
```

Если часть тестов упала, check получает:

```text
status = failed
score = int((passed / total) * 100)
```

Если pytest завершился ошибкой, не собрал тесты, превысил timeout или не смог
сформировать отчет, check получает:

```text
status = error
score = 0
```

### `lint`

Runner запускает Ruff внутри sandbox container.

Настройки в `config_json`:

```json
{
  "entry_file": "solution.py",
  "select": ["F"],
  "ignore": [],
  "line_length": 88
}
```

Что влияет на результат:

- найденные Ruff-нарушения;
- выбранные группы правил `select`;
- исключенные правила `ignore`;
- `line_length`;
- timeout;
- корректность Ruff JSON output.

Score:

- нарушений нет: `100`;
- есть нарушения: `0`;
- ошибка runner/sandbox/config: `0`.

Status:

- нарушений нет: `passed`;
- есть нарушения: `failed`;
- runner не смог корректно выполниться: `error`.

### `static`

Runner выполняет Python AST-проверки без запуска пользовательского кода.

Настройки в `config_json`:

```json
{
  "forbidden_imports": ["os", "subprocess"],
  "forbidden_calls": ["eval", "exec"],
  "required_symbols": ["Solution", "solve"]
}
```

Что влияет на результат:

- запрещенные импорты;
- запрещенные вызовы функций;
- отсутствие обязательных top-level символов;
- syntax error в отправленном коде.

Score:

- findings нет: `100`;
- findings есть: `0`;
- syntax/config/runner error: `0`.

Status:

- findings нет: `passed`;
- findings есть: `failed`;
- ошибка разбора или выполнения runner: `error`.

### `architecture`

Runner выполняет архитектурные AST-проверки Python-кода.

Настройки в `config_json`:

```json
{
  "required_classes": ["OrderService"],
  "required_methods": {
    "OrderService": ["calculate_total"]
  },
  "forbidden_functions": ["process_order"],
  "max_function_length": 20
}
```

Что влияет на результат:

- наличие обязательных классов;
- наличие обязательных методов в классах;
- наличие запрещенных функций;
- длина функций;
- syntax error в отправленном коде.

Score:

- findings нет: `100`;
- findings есть: `0`;
- syntax/config/runner error: `0`.

Status:

- findings нет: `passed`;
- findings есть: `failed`;
- ошибка разбора или выполнения runner: `error`.

## Sandbox и runtime-метрики

Новые Python runner'ы запускаются в Docker sandbox.

На выполнение влияют настройки:

- `CHECKER_SANDBOX_IMAGE`;
- `CHECKER_SANDBOX_CPUS`;
- `CHECKER_SANDBOX_MEMORY`;
- `CHECKER_SANDBOX_PIDS_LIMIT`;
- `CHECKER_SANDBOX_USER`;
- `CHECKER_SANDBOX_TMPFS_SIZE`;
- `CHECKER_SANDBOX_WORKSPACE_TMPFS_SIZE`;
- `CHECKER_SANDBOX_TIMEOUT_OVERHEAD_SECONDS`;
- `CHECKER_SANDBOX_CLEANUP_TIMEOUT_SECONDS`.

Sandbox запускается с ограничениями:

- без сети;
- read-only root filesystem;
- tmpfs для `/tmp`;
- tmpfs для `/workspace`;
- dropped capabilities;
- `no-new-privileges`;
- non-root user.

В `report.metrics` и `report.artifacts` добавляются данные sandbox:

- container image;
- container name;
- exit code;
- duration;
- timeout flags;
- stdout/stderr, обрезанные до лимита.

Важно: runtime-метрики не являются score сами по себе. Они помогают
диагностировать проверку, но баллы выставляет runner.

## Legacy refactor scoring

Если задача использует legacy refactor pipeline, итоговый score считается иначе.

Каждый legacy check имеет:

- `score` - набранные баллы конкретной проверки;
- `max_score` - максимум/вес конкретной проверки;
- `status`.

Формула:

```text
configured = sum(check.max_score)
earned = sum(check.score)
scaled = round((earned / configured) * task.max_score)
result = clamp(scaled, 0, task.max_score)
```

Status legacy pipeline:

- если любая проверка `error`, итоговый status `error`;
- если все проверки `passed`, итоговый status `passed`;
- иначе итоговый status `failed`.

Legacy pipeline сейчас не различает required/optional checks так же гибко, как
новый `TaskCheckSpec` orchestrator.

## Что попадает в API response

После submit backend возвращает краткий ответ:

```json
{
  "submissionId": 123,
  "taskId": 10,
  "status": "passed",
  "score": 100,
  "message": "All tests passed",
  "testPassed": 3
}
```

`message` выбирается так:

- если есть `tests` check и у него есть `report.summary`, используется он;
- если одиночная проверка завершилась error, используется summary ошибки;
- если есть любой error, но не одиночная ошибка, возвращается
  `"Some checks could not be completed"`;
- если есть обязательный failed check, возвращается
  `"Some required checks failed"`;
- иначе возвращается `"All checks passed"`.

`testPassed` берется из `tests.report.passed`. Если tests check отсутствует,
значение будет `0`.

Подробности можно получить через:

```http
GET /api/v1/submissions/{submission_id}
GET /api/v1/submissions/{submission_id}/checks
GET /api/v1/submissions?taskId={task_id}
```

## Как обновляется прогресс пользователя

После каждой отправки вызывается `UserProgressService.record_submission()`.

Для пары user/task хранится `UserTaskProgress`:

- `attempts_count`;
- `first_submission_at`;
- `last_submission_at`;
- `best_submission_id`;
- `is_solved`.

Каждая отправка увеличивает `attempts_count`.

Best submission выбирается так:

1. Больше score лучше.
2. Если score одинаковый, лучше статус с более высоким приоритетом:

```text
passed > failed > error > pending
```

Задача считается решенной, если:

```text
submission.score >= solved_threshold
```

где:

```text
solved_threshold = task.max_score, если 0 < task.max_score <= 100
solved_threshold = 100, иначе
```

`is_solved` монотонен: если задача уже стала solved, более поздняя плохая
отправка не сбросит ее обратно в unsolved.

`User.total_score` пересчитывается как сумма score лучших отправок по задачам:

```text
sum(progress.best_submission.score)
```

Это означает, что частичные баллы за нерешенную задачу тоже могут входить в
общий score пользователя, если такая отправка является лучшей для этой задачи.

## Что влияет на итоговый результат

На итоговые `status`, `score`, progress и отчет влияют:

- наличие `TaskCheckSpec` у задачи;
- типы проверок (`tests`, `lint`, `static`, `architecture`);
- `weight` каждой проверки;
- `is_required` каждой проверки;
- `timeout_seconds`;
- содержимое `config_json`;
- фактический пользовательский код;
- выбранный язык решения;
- `task.max_score`;
- корректность sandbox/container execution;
- ошибки синтаксиса;
- ошибки runner;
- порядок проверок влияет на порядок сохранения/отображения, но не на формулу
  score.

## Практические рекомендации для задач

Для задач с частичным оцениванием:

- используйте несколько pytest-тестов;
- задавайте `weight` так, чтобы важные проверки сильнее влияли на итог;
- делайте style/lint проверки optional, если они не должны валить всю отправку;
- делайте tests required, если провал функциональности должен давать
  `status=failed`;
- используйте `task.max_score=100`, если хотите стандартную шкалу процентов.

Для задач, где статус должен быть строгим:

- помечайте ключевые проверки `is_required=True`;
- не полагайтесь только на score;
- используйте static/architecture проверки как required, если нарушение
  архитектуры должно валить submission.

Для задач, где важен UX частичного прогресса:

- разрешайте частичный pytest score;
- учитывайте, что failed submission с partial score может стать best submission;
- помните, что partial best score попадет в `User.total_score`.

## Примеры

### Полный успех

```text
tests: required, score=100, weight=100, status=passed

Submission.status = passed
Submission.score = 100
Progress: solved=true
```

### Частичный pytest

```text
tests: required, 1/3 tests passed, score=33, weight=100, status=failed

Submission.status = failed
Submission.score = 33
Progress: solved=false
User.total_score includes 33 if it is the best submission for this task
```

### Optional lint failed

```text
tests: required, score=100, weight=75, status=passed
lint: optional, score=0, weight=25, status=failed

Submission.status = passed
Submission.score = 75
Progress: solved=false when task.max_score=100
```

### Required architecture failed

```text
tests: required, score=100, weight=70, status=passed
architecture: required, score=0, weight=30, status=failed

Submission.status = failed
Submission.score = 70
Progress: solved=false when task.max_score=100
```

### Runner error

```text
tests: required, status=error, score=0

Submission.status = error
Submission.score = 0
Progress: solved=false
```
