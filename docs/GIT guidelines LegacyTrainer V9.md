# LegacyTrainer — Git Workflow

## 1. Основные ветки

### `main`
- Содержит стабильную и проверенную версию проекта.
- Merge разрешается только через Pull Request из веток `develop` или `hotfix/*`.
- Прямые коммиты запрещены.

### `develop`
- Интеграционная ветка для всех feature-веток.
- Merge из feature-веток осуществляется только через Pull Request.
- После стабилизации `develop` выполняется merge в `main`.

---

## 2. Feature-ветки

### Создание
- Создаются от ветки `develop` для реализации одной задачи.
- Перед созданием ветки необходимо актуализировать `develop`:
```bash
git checkout develop
git pull
git checkout -b feature/<модуль>/<краткое-описание>
```
- Продолжительность жизни ветки должна быть минимальной.

### Модули
- `frontend` — интерфейс и UI
- `backend` — бизнес-логика
- `ai-agent` — логика ИИ для оценки кода
- `docs` — документация

### Синхронизация с develop
- **Регулярная:** Рекомендуется ежедневно обновлять feature-ветку из `develop`.
- **Обязательная перед PR:** Перед созданием Pull Request необходимо убедиться, что ветка актуальна.
- **Действия при обновлении `develop` во время разработки:**
    1. Обновите локальный `develop`: `git checkout develop && git pull`.
    2. Влейте изменения в feature-ветку: `git checkout feature/<name> && git merge develop`.
    3. Разрешите конфликты локально (см. раздел 8).
    4. Проверьте сборку и тесты.
    5. Отправьте изменения: `git push`.
- PR с конфликтами или устаревшей веткой не принимается.

### Примеры имен
```
feature/frontend/login-ui
feature/backend/auth-api
feature/ai-agent/evaluation-logic
feature/tests/auth-integration
feature/docs/readme-update
```

### Правила
- Каждая ветка отражает **одну задачу**.
- Merge в `develop` исключительно через Pull Request.
- После успешного merge ветка удаляется.
- Feature-ветки не должны зависеть друг от друга.

### Особые случаи: зависимые задачи
Если задача логически зависит от другой:
- В описании PR указывается зависимость.
- Перед слиянием в `develop` дождаться вливания родительской ветки.
- Перебазировать дочернюю ветку на актуальный `develop`.
- Для совместного тестирования использовать временную интеграционную ветку.

#### Пример зависимых задач
1. **Родительская ветка**: `feature/backend/auth-api`
2. **Дочерняя ветка**: `feature/frontend/login-ui` (создана от `auth-api`)
3. **Описание PR**: «Зависит от #123 (feature/backend/auth-api)».
4. **Порядок слияния**:
   - Влить `auth-api` в `develop`.
   - Обновить `login-ui`: `git checkout feature/frontend/login-ui && git merge develop`.
   - Влить `login-ui` в `develop`.

---

## 3. Hotfix-ветки

### Создание
- Создаются от ветки `main` при обнаружении критических ошибок.

### Формат имени
```
hotfix/<краткое-описание>
```

### Примеры
```
hotfix/login-crash
hotfix/evaluation-bug
```

### Правила
- После исправления выполняется merge в ветки: `main`, `develop`.
- Срок жизни ветки минимальный.
- Подветки запрещены.

---
## 4. tests - ветки
### Создание
* Ветки tests являются производными от веток feature/hotfix.

```bash
git pull
git checkout feature/<модуль>/<краткое-описание>
# в случае если на ветке произошли изменения
git pull
# ------------------------------------------
git checkout -b tests/<модуль>/<краткое-описание>
```
### Формат имени
```
tests/<модуль>/<краткое-описание>
```
### Примеры

```
tests/backend/auth-api-tests  
tests/frontend/login-ui-tests  
tests/ai-agent/evaluation-tests
```
### Модули
- `frontend` — интерфейс и UI
- `backend` — бизнес-логика
- `ai-agent` — логика ИИ для оценки кода
### Процесс работы

1. Разработка тестов ведётся в `tests/*` ветке.
2. В описании PR обязательно указывается зависимость от feature/hotfix ветки:
    
    ```
    Depends on: feature/backend/auth-api
    ```
    
1. При изменениях в родительской ветке:
    ```bash
    git checkout tests/<...>  
    git merge feature/<...>
    ```

### Порядок PR

1. Сначала создается PR для родительской ветки.
2. После слияния родительской ветки с develop создается PR для дочерней ветки
---
## 5. Коммиты

### Формат
```
<тип>[опциональная_область]: <краткое описание>
[опциональное подробное описание]
```

### Типы
|Тип|Описание|
|---|---|
|`feat`|Новая функциональность|
|`fix`|Исправление ошибки|
|`docs`|Изменения в документации|
|`style`|Форматирование кода|
|`refactor`|Рефакторинг кода|
|`perf`|Улучшение производительности|
|`test`|Добавление или исправление тестов|
|`chore`|Изменения в сборке/инфраструктуре|

### Примеры
```
feat[auth]: login endpoint added
fix[auth]: fixed token verification
docs[readme]: updated the README documentation
```

### Правила
1. Один логический шаг = один коммит.
2. Коммит должен быть атомарным.
3. Заголовок коммита ≤ 72 символов.
4. Описание на английском языке.
5. Использовать области в квадратных скобках (`feat[auth]: ...`).

---

## 6. Pull Request
## For Feature/Hotfix branches
### Title
```
<module>: <Short description>
```
### Description:
```
What is implemented and why.
``` 
#### List of changes:
```
Add all the commits on the branch
```
#### Module:
```
module: <name>
```
#### Testing:
```
Write the testing methods in this block
```
## For tests branches

### Title
```
<module>: <Short description>
```
### Description:
```
What is implemented and why.
``` 
#### List of changes:
```
Add all the commits on the branch
```
#### Depends on: 
```
feature/<module>/<short-description>
```
#### Module:
```
module: <name>
```

### Требования к PR
- Минимум один approval.
- Merge только после успешного тестирования(кроме tests веток).
- После merge ветка удаляется.
- **Конфликты должны быть разрешены до создания Pull Request.**
- Описание на английском языке.

---

## 7. Процесс ветвления

```
feature/* → develop → main
tests/* → feature/* → develop → main
hotfix/* → main → develop
```

---

## 8. Общие требования

1. Прямой push в `main` и `develop` запрещён.
2. Каждый commit информативный и атомарный.
3. Описание commit и PR на английском языке.
4. Соблюдать модульную ответственность.
5. У каждого модуля должен быть ответственный ревьюер.

---

## 9. Разрешение конфликтов

Применяется ко всем типам веток (`feature/*`, `hotfix/*`).

**Алгоритм:**
1. Обновите целевую ветку:
   ```bash
   git checkout <target>
   git pull
   ```
2. В рабочей ветке выполните слияние:
   ```bash
   git checkout <branch>
   git merge <target>
   ```
3. Исправьте конфликты в файлах, отметьте решёнными:
   ```bash
   git add <file>
   git commit
   ```
4. Проверьте сборку и тесты.
5. Отправьте изменения:
```bash
   git push
```
 
**Правила:**
- Конфликты устраняются **локально автором ветки** до создания PR.
- Запрещено перекладывать решение конфликтов на ревьюера.
- Если конфликты сложные, запросите помощь до открытия PR.