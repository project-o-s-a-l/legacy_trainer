# Code Checking Implementation

Этот документ описывает, как именно в проекте реализована проверка кода:
какой API запускает проверку, как backend выбирает механизм проверки, как
запускается sandbox, какие runner'ы существуют, что они проверяют и где это
реализовано в коде.

Соседний документ `docs/checker-scoring-and-results.md` описывает оценивание и
расчет score. Этот документ больше про технический pipeline выполнения.

## Главные файлы реализации

API и orchestration:

- `backend/app/api/v1/submissions.py` - HTTP endpoints для отправки решения,
  получения submission, checks и истории.
- `backend/app/services/submission.py` - основной сервис отправки решения:
  validation, выбор checker pipeline, сохранение результата.
- `backend/app/services/checking/orchestrator.py` - orchestrator новой
  `TaskCheckSpec`-системы.
- `backend/app/services/checking/types.py` - внутренние контракты проверки:
  `CheckContext`, `CheckRunResult`, `CheckRunner`,
  `CheckOrchestrationResult`.
- `backend/app/models/task_check_spec.py` - модель настройки проверки задачи.
- `backend/app/schemas/check.py` - Pydantic-контракты report/spec/check result.

Sandbox и runner'ы:

- `backend/app/services/checking/sandbox.py` - Docker sandbox executor.
- `backend/app/services/checking/sandboxed_runner.py` - общий wrapper для
  sandboxed checks.
- `backend/app/services/checking/python_pytest_runner.py` - runner для pytest.
- `backend/app/services/checking/python_lint_runner.py` - runner для Ruff.
- `backend/app/services/checking/python_static_runner.py` - runner для static и
  architecture AST checks.
- `legacy_checker/run.py` - entrypoint внутри checker container.
- `legacy_checker/checks.py` - фактическая логика pytest/lint/static/architecture
  проверок внутри sandbox.
- `docker/checker.Dockerfile` - Docker image для `legacy-trainer-checker:local`.

Legacy refactor pipeline:

- `backend/app/services/refactor_checks/pipeline.py`
- `backend/app/services/refactor_checks/behavior_checker.py`
- `backend/app/services/refactor_checks/contract_checker.py`
- `backend/app/services/refactor_checks/structure_checker.py`
- `backend/app/services/refactor_checks/quality_checker.py`

Docker/compose:

- `compose.yaml` - сервисы `docker-daemon`, `sandbox-prep`, `backend`,
  `frontend`, `postgres`.
- `backend/app/core/config.py` - env settings для checker и legacy Docker
  runners.

## Entry point: отправка решения

Проверка запускается через endpoint:

```http
POST /api/v1/tasks/{task_id}/submit
```

Endpoint находится в `backend/app/api/v1/submissions.py`.

Он принимает `SubmissionCreateRequest`:

```json
{
  "code": "...",
  "language": "python"
}
```

и вызывает:

```python
SubmissionService(db).submit(...)
```

Основная логика находится в `backend/app/services/submission.py`.

## Что делает `SubmissionService.submit`

`SubmissionService.submit` выполняет несколько шагов.

### 1. Проверяет задачу

Сервис получает задачу через `TaskRepository.get_task_by_id`.

Если задачи нет:

```text
404 Task not found
```

### 2. Проверяет код

Код очищается через:

```python
code = data.code.strip()
```

Если после trim код пустой:

```text
422 Code must not be empty
```

### 3. Нормализует язык

Поддерживаемые алиасы сейчас:

```python
{
    "python": ("python", "Python"),
    "cpp": ("cpp", "C++"),
    "c++": ("cpp", "C++"),
}
```

Если язык неизвестен:

```text
400 Unsupported language
```

### 4. Проверяет, доступен ли язык для задачи

Даже если язык в системе есть, он должен быть привязан к задаче через
`task.languages`.

Если выбранный язык не доступен для задачи:

```text
400 Language is not available for this task
```

### 5. Создает `Submission`

Создается запись со статусом `pending`:

```python
self.submissions.create_submission(...)
```

На этом этапе у submission уже есть `id`, который затем используется в names и
metadata sandbox-контейнеров.

### 6. Запускает проверки

Сервис вызывает:

```python
orchestration = self._run_checks(...)
```

Именно `_run_checks` выбирает, какой механизм проверки использовать.

### 7. Сохраняет итоговые поля submission

После проверки сервис записывает:

```python
submission.status = orchestration.status
submission.score = orchestration.score
submission.checked_at = orchestration.checked_at
submission.memory_used_kb = orchestration.memory_used_kb
submission.execution_time_ms = orchestration.execution_time_ms
```

### 8. Сохраняет все отдельные checks

Для каждого `CheckRunResult` создается `SubmissionCheck`:

```python
self.submissions.create_submission_check(
    submission_id=submission.id,
    check_type=check.check_type,
    status=check.status,
    score=check.score,
    report_json=check.to_report_json(),
)
```

Это важно: итоговый submission хранит aggregate result, а подробные проверки
хранятся отдельно.

### 9. Обновляет progress

После сохранения checks вызывается:

```python
self.progress.record_submission(...)
```

Это обновляет попытки, best submission, solved state и total score.

## Как выбирается механизм проверки

Выбор происходит в `SubmissionService._run_checks`.

Порядок:

```text
1. Если у task есть check_specs -> новая TaskCheckSpec-система.
2. Иначе попробовать legacy RefactorCheckPipeline.
3. Если legacy pipeline не применим -> deterministic no-spec fallback.
```

В коде это выглядит концептуально так:

```python
if task.check_specs:
    return self.check_orchestrator.run(context)

pipeline_result = self.refactor_pipeline.evaluate(...)
if pipeline_result is not None:
    return self._orchestration_from_refactor_pipeline(...)

return self.check_orchestrator.run(context)
```

## `CheckContext`

Перед запуском проверки создается `CheckContext`.

Он определен в `backend/app/services/checking/types.py`:

```python
class CheckContext:
    task: Task
    submission: Submission
    program_language: ProgramLanguage
    source_code: str
```

Этот объект передается runner'ам, чтобы они знали:

- какую задачу проверяют;
- какую отправку проверяют;
- на каком языке код;
- какой именно source code надо проверить.

## Новая система `TaskCheckSpec`

`TaskCheckSpec` описывает одну проверку задачи.

Модель находится в `backend/app/models/task_check_spec.py`.

Поля:

```python
id
task_id
check_type
name
weight
timeout_seconds
is_required
order
config_json
```

Основные поля для выполнения:

- `check_type` выбирает runner.
- `timeout_seconds` ограничивает время выполнения.
- `config_json` передается runner'у как настройки.
- `order` влияет на порядок запуска.
- `weight` и `is_required` влияют на aggregate result.

Типы check'ов берутся из enum `SubmissionCheckType`:

- `tests`
- `lint`
- `static`
- `architecture`

## `CheckOrchestrator`

Orchestrator находится в:

```text
backend/app/services/checking/orchestrator.py
```

Он отвечает за:

- сортировку check specs;
- выбор runner'а по `check_type`;
- запуск каждой проверки;
- fallback, если specs нет;
- aggregate status;
- aggregate score;
- aggregate time/memory;
- response message;
- количество passed tests.

### Регистрация default runners

В `CheckOrchestrator.with_default_runners()` зарегистрированы:

```python
{
    SubmissionCheckType.TESTS: PythonPytestRunner(),
    SubmissionCheckType.LINT: PythonRuffLintRunner(),
    SubmissionCheckType.STATIC: PythonStaticRunner(),
    SubmissionCheckType.ARCHITECTURE: PythonArchitectureRunner(),
}
```

Если у задачи нет check specs, используется:

```python
no_spec_tests_runner=DeterministicFakeRunner(SubmissionCheckType.TESTS)
```

### Порядок выполнения specs

Specs сортируются так:

```python
sorted(context.task.check_specs, key=lambda spec: (spec.order, spec.id))
```

Это значит, что сначала учитывается `order`, а при равенстве - `id`.

### Что если runner отсутствует

Если для `check_type` нет runner'а, orchestrator возвращает error-result:

```text
status = error
score = 0
summary = "No runner registered for ..."
```

Такой check сохраняется как обычный `SubmissionCheck`, но с ошибкой.

## Контракт runner'а

Runner реализует protocol `CheckRunner`:

```python
def run(
    *,
    context: CheckContext,
    spec: TaskCheckSpec | None,
) -> CheckRunResult:
    ...
```

Результат runner'а - `CheckRunResult`:

```python
check_type
status
score
report
spec_id
name
weight
is_required
execution_time_ms
memory_used_kb
```

`report` должен быть объектом `CheckReport`.

## `CheckReport`

`CheckReport` описан в `backend/app/schemas/check.py`.

Структура:

```python
total: int
passed: int
failed: int
errors: int
summary: str | None
details: list[CheckReportDetail]
metrics: dict[str, Any]
artifacts: dict[str, Any]
```

`details` содержит отдельные тест-кейсы или найденные нарушения:

```python
name
status
message
path
line
column
details
```

`metrics` обычно содержит структурированные данные выполнения:

- runner name;
- duration;
- timeout;
- config values;
- sandbox/container metadata.

`artifacts` содержит вывод и технические артефакты:

- stdout;
- stderr;
- exit code;
- duration;
- timeout flags.

## Как запускается sandbox

Новые Python checks запускаются через общий `SandboxedCheckRunner`.

Файл:

```text
backend/app/services/checking/sandboxed_runner.py
```

Конкретные runner'ы `PythonPytestRunner`, `PythonRuffLintRunner`,
`PythonStaticRunner`, `PythonArchitectureRunner` тонкие: они только задают
`check_type` и наследуют поведение `SandboxedCheckRunner`.

### Подготовка payload

`SandboxedCheckRunner.run` формирует `SandboxExecutionRequest`.

В `payload` передается:

```json
{
  "check_type": "tests",
  "check_name": "pytest",
  "timeout_seconds": 10,
  "program_language": "python",
  "source_code": "...",
  "config": {
    "entry_file": "solution.py",
    "test_file": "test_solution.py",
    "test_code": "...",
    "visible": false
  }
}
```

То есть код пользователя не монтируется файлом с host. Он сериализуется в JSON,
передается в stdin контейнера, а внутри контейнера записывается во временный
workspace.

### Docker executor

Docker executor находится в:

```text
backend/app/services/checking/sandbox.py
```

Класс:

```python
DockerSandboxExecutor
```

Он запускает:

```text
docker run ...
```

и передает payload через stdin.

Команда включает ограничения:

```text
--rm
--network none
--cpus ...
--memory ...
--pids-limit ...
--read-only
--tmpfs /tmp
--tmpfs /workspace
--cap-drop ALL
--security-opt no-new-privileges
--user 10001:10001
--workdir /workspace
-i legacy-trainer-checker:local
```

Контейнер получает labels:

```text
legacy-trainer.checker=true
legacy-trainer.check-type=<type>
```

Имя контейнера формируется примерно так:

```text
legacy-trainer-check-<check_type>-<submission_id>-<spec_id>-<random>
```

Так как используется `--rm`, после успешной проверки контейнер удаляется.

### Timeout

Sandbox timeout считается так:

```python
request.timeout_seconds + checker_sandbox_timeout_overhead_seconds
```

Если процесс не завершился вовремя:

- контейнер удаляется через `docker rm -f`;
- check получает `status=error`;
- score становится `0`;
- в report пишется timeout/error metadata.

## Где выполняется Docker

В docker compose используется отдельный Docker-in-Docker сервис:

```yaml
docker-daemon:
  image: docker:28-dind
```

Backend получает:

```yaml
DOCKER_HOST: tcp://docker-daemon:2375
```

Поэтому sandbox-контейнеры создаются внутри `legacy-trainer-docker-daemon-1`,
а не напрямую в host Docker daemon.

Сервис `sandbox-prep` одноразовый:

```yaml
sandbox-prep:
  image: docker:28-cli
  command:
    docker build ...
```

Он собирает образы:

- `legacy-trainer-python-runner:latest`;
- `legacy-trainer-cpp-runner:latest`;
- `legacy-trainer-checker:local`.

После успешной сборки `sandbox-prep` завершает работу с `Exited (0)`. Это
ожидаемое состояние.

## Checker container

Docker image для новой системы описан в:

```text
docker/checker.Dockerfile
```

Он:

1. Берет `python:3.12-slim`.
2. Создает non-root пользователя `checker` с uid `10001`.
3. Устанавливает `pytest` и `ruff`.
4. Копирует `legacy_checker` в `/opt/legacy_checker`.
5. Выставляет `PYTHONPATH=/opt`.
6. Запускает:

```text
python -m legacy_checker.run
```

Entrypoint:

```text
legacy_checker/run.py
```

Он читает JSON из stdin:

```python
payload = json.loads(sys.stdin.read() or "{}")
```

затем вызывает:

```python
run_check(payload)
```

из `legacy_checker/checks.py`, после чего печатает JSON result в stdout.

## Как backend обрабатывает ответ sandbox

`SandboxedCheckRunner._from_sandbox_result` разбирает результат.

Возможные случаи:

### Sandbox вернул executor error

Например Docker недоступен, timeout, container error.

Результат:

```text
CheckStatus.ERROR
score = 0
report.summary = текст ошибки
```

### Container exit code не 0

Если container завершился неуспешно на уровне процесса:

```text
CheckStatus.ERROR
score = 0
```

### stdout не JSON

Если stdout нельзя распарсить как JSON:

```text
CheckStatus.ERROR
score = 0
summary = "Sandbox output could not be parsed as JSON"
```

### JSON не объект

Если checker вернул не объект:

```text
CheckStatus.ERROR
score = 0
summary = "Sandbox output JSON must be an object"
```

### report невалидный

Если `report` не проходит `CheckReport.model_validate`:

```text
CheckStatus.ERROR
score = 0
summary = "Sandbox result report failed validation"
```

### Валидный результат

Если все корректно:

- `status` берется из JSON;
- `score` ограничивается диапазоном `0..100`;
- `report` валидируется;
- в `report.metrics` и `report.artifacts` добавляется sandbox metadata;
- создается `CheckRunResult`.

## Что проверяет `tests`

Реализация:

```text
legacy_checker/checks.py -> _run_pytest
```

Runner:

```text
backend/app/services/checking/python_pytest_runner.py
```

### Конфигурация

Ожидаемый `config_json`:

```json
{
  "entry_file": "solution.py",
  "test_file": "test_solution.py",
  "test_code": "...",
  "visible": false
}
```

Проверяется:

- `entry_file` должен быть локальным `.py` файлом;
- `test_file` должен быть локальным `.py` файлом;
- `test_code` должен быть непустой строкой;
- `visible` должен быть boolean.

### Как выполняется

Внутри container:

1. Source code пользователя записывается в `entry_file`.
2. Тестовый код из `config_json.test_code` записывается в `test_file`.
3. Запускается:

```text
python -m pytest <test_file> --junitxml=pytest-report.xml --tb=short -q
```

4. JUnit XML парсится через `xml.etree.ElementTree`.
5. Из XML считаются:

- total;
- passed;
- failed;
- errors;
- skipped;
- details по test cases.

### Что считается passed/failed/error

Если pytest не создал JUnit report:

```text
status=error
score=0
```

Если есть pytest errors:

```text
status=error
score=0
```

Если pytest не собрал тесты и returncode не 0:

```text
status=error
score=0
```

Если есть failed tests:

```text
status=failed
score=int((passed / total) * 100)
summary="<passed> of <total> tests passed"
```

Если все тесты прошли:

```text
status=passed
score=100
summary="All tests passed"
```

### Что попадает в details

Для каждого testcase создается detail:

- `name` - classname + test name;
- `status` - `passed`, `failed` или `error`;
- `message` - сообщение failure/error, если есть;
- `path`;
- `line`;
- `details.runner = python_pytest`;
- `details.classname`;
- `details.time`;
- `details.skipped`.

## Что проверяет `lint`

Реализация:

```text
legacy_checker/checks.py -> _run_ruff
```

Runner:

```text
backend/app/services/checking/python_lint_runner.py
```

### Конфигурация

Пример:

```json
{
  "entry_file": "solution.py",
  "select": ["F"],
  "ignore": [],
  "line_length": 88
}
```

Проверяется:

- `entry_file` должен быть локальным `.py` файлом;
- `select` должен быть списком строк;
- `ignore` должен быть списком строк;
- `line_length`, если указан, должен быть положительным integer.

### Как выполняется

Внутри container:

1. Source code пользователя записывается в `entry_file`.
2. Запускается Ruff:

```text
python -m ruff check <entry_file> --output-format=json --no-cache
```

3. Если указаны `select`, `ignore`, `line_length`, они добавляются как CLI
   options.
4. JSON output Ruff парсится.

### Что проверяется

Ruff проверяет код по выбранным правилам. Например `select=["F"]` включает
pyflakes-подобные ошибки: неопределенные имена, неиспользуемые импорты и т.п.

### Результат

Если Ruff output не JSON:

```text
status=error
score=0
```

Если Ruff нашел findings:

```text
status=failed
score=0
```

Если findings нет и returncode 0:

```text
status=passed
score=100
summary="Lint passed"
```

### Что попадает в details

Для каждого finding:

- `name` - код Ruff rule, например `F821`;
- `status=failed`;
- `message` - сообщение Ruff;
- `path` - файл;
- `line`;
- `column`;
- `details.runner = python_ruff_lint`;
- `details.code`;
- `details.url`.

## Что проверяет `static`

Реализация:

```text
legacy_checker/checks.py -> _run_static
```

Runner:

```text
backend/app/services/checking/python_static_runner.py`
```

### Конфигурация

Пример:

```json
{
  "forbidden_imports": ["os", "subprocess"],
  "forbidden_calls": ["eval", "exec"],
  "required_symbols": ["Solution", "solve"]
}
```

### Как выполняется

Runner не запускает код пользователя. Он парсит source code через:

```python
ast.parse(source_code)
```

Затем обходит AST.

### Что проверяется

`forbidden_imports`:

- запрещает `import os`;
- запрещает `import os.path`;
- запрещает `from os import path`;
- учитывает root module.

`forbidden_calls`:

- запрещает вызовы функций;
- проверяет простые вызовы вроде `eval(...)`;
- проверяет attribute calls вроде `module.eval(...)`, если имя совпадает с
  запрещенным suffix.

`required_symbols`:

- проверяет top-level классы;
- top-level функции;
- async функции;
- переменные из assign/annassign;
- импортированные имена.

### Результат

Если AST findings есть:

```text
status=failed
score=0
summary="Static checks found N issue(s)"
```

Если findings нет:

```text
status=passed
score=100
summary="Static checks passed"
```

Если код нельзя распарсить:

```text
status=error
score=0
summary="Syntax error: ..."
```

### Типы findings

Возможные `detail.name`:

- `forbidden_import`;
- `forbidden_call`;
- `required_symbol`;
- `syntax_error`.

## Что проверяет `architecture`

Реализация:

```text
legacy_checker/checks.py -> _run_architecture
```

Runner:

```text
backend/app/services/checking/python_static_runner.py
```

Там объявлены два класса:

- `PythonStaticRunner`;
- `PythonArchitectureRunner`.

### Конфигурация

Пример:

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

### Как выполняется

Код парсится через `ast.parse`, затем runner:

1. Собирает все классы.
2. Проверяет обязательные классы.
3. Проверяет обязательные методы внутри классов.
4. Обходит функции и async functions.
5. Проверяет запрещенные имена функций.
6. Считает длину функций через `end_lineno - lineno + 1`.

### Что проверяется

`required_classes`:

- каждый класс из списка должен существовать в AST.

`required_methods`:

- для указанного класса должны существовать методы с заданными именами.

`forbidden_functions`:

- функции с такими именами запрещены.

`max_function_length`:

- если функция длиннее лимита, создается finding.

### Результат

Если findings есть:

```text
status=failed
score=0
summary="Architecture checks found N issue(s)"
```

Если findings нет:

```text
status=passed
score=100
summary="Architecture checks passed"
```

Если код нельзя распарсить:

```text
status=error
score=0
```

### Типы findings

Возможные `detail.name`:

- `required_class`;
- `required_method`;
- `forbidden_function`;
- `max_function_length`;
- `syntax_error`.

## Как сохраняются результаты

Итоговый результат сохраняется в таблице `submission`.

Отдельные проверки сохраняются в `submission_check`.

Публичные endpoints:

```http
GET /api/v1/submissions/{submission_id}
GET /api/v1/submissions/{submission_id}/checks
GET /api/v1/submissions?taskId={task_id}
```

`GET /api/v1/submissions/{submission_id}/checks` возвращает checks,
отсортированные по `id`.

История `GET /api/v1/submissions?taskId=...` возвращает только submissions
текущего пользователя и сортирует их так:

```text
submitted_at desc, id desc
```

## Legacy refactor pipeline

Если у задачи нет `TaskCheckSpec`, backend пробует legacy refactor pipeline.

Файл:

```text
backend/app/services/refactor_checks/pipeline.py
```

Он строит task definition из:

- `TaskScenario`;
- `TaskCheckRule`.

Затем запускает проверки по rule type:

- `behavior`;
- `contract`;
- `structure`;
- `quality`.

### Behavior check

Behavior checker сравнивает поведение legacy code и candidate code на
сценариях задачи.

Для Python это может быть проверка функции.
Для C++ это может быть stdin/stdout сценарий.

Результат сохраняется как check type `tests`.

### Contract check

Проверяет, что код сохраняет ожидаемый контракт.

Например:

- обязательные функции;
- обязательные токены;
- ожидаемые публичные элементы.

Результат сохраняется как check type `static`.

### Structure check

Проверяет структурные ограничения.

Например:

- обязательные токены;
- запрет global assignments;
- ограничение top-level statements;
- минимальное количество классов.

Результат сохраняется как check type `architecture`.

### Quality check

Проверяет простые quality-маркеры.

Например:

- `TODO`;
- `pass`;
- `NotImplementedError`;
- другие запрещенные markers.

Результат сохраняется как check type `lint`.

### Адаптация legacy результата

`SubmissionService._orchestration_from_refactor_pipeline` преобразует
`PipelineResult` в общий `CheckOrchestrationResult`.

Каждый `CheckOutcome` преобразуется в `CheckRunResult`.

Legacy reports нормализуются в общий `CheckReport` shape, чтобы API checks
возвращал единый формат для новой и старой систем.

## Deterministic fallback

Если у задачи нет `TaskCheckSpec` и legacy pipeline вернул `None`, запускается
orchestrator без specs.

В этом случае используется:

```python
DeterministicFakeRunner(SubmissionCheckType.TESTS)
```

Это резервный механизм, который имитирует basic tests behavior. Он нужен, чтобы
старые или минимально настроенные задачи продолжали возвращать результат.

Для новых задач лучше явно создавать `TaskCheckSpec`.

## Какие ошибки чаще всего влияют на проверку

### Ошибка конфигурации check spec

Например:

- `tests.config_json.test_code` пустой;
- `entry_file` не `.py`;
- `line_length` не positive integer;
- `required_methods` не объект нужной структуры.

Результат:

```text
check.status = error
check.score = 0
```

Если check required:

```text
submission.status = error
```

### Ошибка синтаксиса в пользовательском коде

Для `static` и `architecture` syntax error возникает на `ast.parse`.

Для `tests` syntax error обычно проявляется через pytest errors.

Результат обычно:

```text
status = error
score = 0
```

### Timeout

Timeout может случиться:

- внутри pytest/Ruff subprocess;
- на уровне Docker sandbox executor.

Результат:

```text
status = error
score = 0
```

В report пишутся поля `timedOut`, `timeout_seconds`, duration и container
metadata.

### Docker/sandbox unavailable

Если backend не может запустить Docker:

```text
Docker executable not found
Sandbox executor failed
Sandbox container exited with code ...
```

Результат:

```text
status = error
score = 0
```

## Как отлаживать проверку

### Посмотреть compose-сервисы

```powershell
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
```

`legacy-trainer-sandbox-prep-1` должен быть `Exited (0)` после успешной сборки
образов.

`legacy-trainer-docker-daemon-1` должен быть `Up` и `healthy`.

### Посмотреть образы внутри DinD daemon

```powershell
docker exec legacy-trainer-docker-daemon-1 docker images
```

Ожидаемые образы:

- `legacy-trainer-checker:local`;
- `legacy-trainer-python-runner:latest`;
- `legacy-trainer-cpp-runner:latest`.

### Посмотреть running checker containers

Так как контейнеры запускаются с `--rm`, они быстро исчезают.
Во время проверки можно выполнить:

```powershell
docker exec legacy-trainer-docker-daemon-1 docker ps --filter label=legacy-trainer.checker=true
```

### Посмотреть подробный отчет проверки

Через API:

```http
GET /api/v1/submissions/{submission_id}/checks
```

В ответе смотреть:

- `status`;
- `score`;
- `report.summary`;
- `report.details`;
- `report.metrics`;
- `report.artifacts`.

## Краткая последовательность выполнения новой проверки

```text
User submits code
  -> FastAPI endpoint /tasks/{task_id}/submit
  -> SubmissionService.submit
  -> create Submission(pending)
  -> SubmissionService._run_checks
  -> CheckOrchestrator.run
  -> sort TaskCheckSpec by (order, id)
  -> for each spec choose runner by check_type
  -> SandboxedCheckRunner.run
  -> DockerSandboxExecutor.execute
  -> docker run legacy-trainer-checker:local
  -> legacy_checker.run reads JSON stdin
  -> legacy_checker.checks.run_check
  -> _run_pytest / _run_ruff / _run_static / _run_architecture
  -> checker prints JSON result to stdout
  -> backend parses and validates CheckReport
  -> backend enriches report with sandbox metadata
  -> CheckOrchestrator aggregates checks
  -> SubmissionService saves Submission fields
  -> SubmissionService saves all SubmissionCheck rows
  -> UserProgressService updates progress and total_score
  -> API returns SubmissionCreateResponse
```
