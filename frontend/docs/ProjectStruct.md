# LegacyTrainer - структура директорий frontend
### Глобальные вещи (Файлы/директории):
То, что влияет на всё приложение, не должно лежать внутри страницы или виджета
К примеру:
- Глобальные CSS-стили / переменные;
- Theme provider;
- API Client;

Также есть файлы index.ts - часто используется как единая точка экспорта из папки. Часто используются в папках компонентов, страниц, виджетов и фич как удобная точка входа для импортов.
Скрывает внутреннюю структуру папки и делает импорт короче.  
# **ВАЖНО:**
В примерах, импорты везде считать по принципу работы через index.ts  
Пример кода: [index.ts](./ProjectStructExamples.md#index-ts)
index.html - HTML entry point Vite

---
## src
Основная директория проекта. Внутри находятся TSX-, TS- и CSS-файлы, а также основные слои архитектуры.
Обязательно здесь находится точка входа в приложение (main.tsx).
### Подробно:
#### main:
main.tsx - клиентская точка входа приложения
Что обычно происходит:
- Импортируется глобальный CSS;
- Подключается App;
- Рендерится React root;  
- Пример кода: Не нуждается, т.к. с большой вероятностью он останется шаблонным
---
## app
Слой приложения целиком. В app размещается код, который относится ко всему приложению целиком.
### Подробно:
#### App.tsx:
Корневой компонент приложения. Внутри обычно:
- layout-обёртка;
- провайдеры;
- router rendering;
- глобальные boundary-компоненты;
Пример кода: [App.tsx](./ProjectStructExamples.md#app-tsx)
#### providers:
Глобальные провайдеры
##### router:
Все что связано с маршрутизацией:
- renderRoutes.tsx - генерация \<Route /> 
    - Пример кода: [renderRoutes.tsx](./ProjectStructExamples.md#renderRoutes-tsx)
- routeConfig.ts - полная конфигурация маршрутов для роутинга и Navbar
    - Пример кода: [routeConfig.ts](./ProjectStructExamples.md#routeConfig-ts)
#### styles
Глобальные стили проекта
##### ./*.css
- index.css: Главный CSS-файл, импортирует остальные глобальные стили
    - Пример кода: [index.css](./ProjectStructExamples.md#globalcss)
- variables.css: 
    - цвета;
    - отступы;
    - ширина контейнера;
    - размеры шрифтов;
    - радиусы;
        - Пример кода: [variable.css](./ProjectStructExamples.md#variablecss)
- typography.css: общие стили типографики
#### config
- env.ts - чтение и нормализация env-переменных
    - Пример кода: [env.ts](./ProjectStructExamples.md#env-ts)
---
## pages
Каждая папка в pages обычно соответствует одной странице маршрута
Помещайте код в pages, только если он соответствует отдельной странице приложения и связан с конкретным маршрутом.
### Подробно:
- Соответствует маршруту;
- Собирает крупные блоки;
- Может подключать widgets и features;
- Пример кода: [pages.tsx](./ProjectStructExamples.md#pages-tsx)
---
## widgets
Это крупные самостоятельные визуальные блоки интерфейса, которые можно вставлять в страницы
Обычно:
- Navbar;
- Footer;
- Sidebar;
- Примеры кода: [widgets.tsx](./ProjectStructExamples.md#widgets-tsx)
---
## features
Пользовательские сценарии и бизнес-логика.
Сюда кладут всё, что связано с действиями пользователя и бизнес-сценариями.
- login;
- search;
- switch theme;
- filters;
### Внутренняя структура:
#### ui
- Формы;
- Кнопки действий;
- модалки;
- Пример кода: [features/ui.tsx](./ProjectStructExamples.md#features-ui-tsx)
#### model
Внутренняя логика фичи:
- типы;
- хуки;
- slice;
- selectors;
- state;
- Пример кода: [features/model.ts](./ProjectStructExamples.md#features-model-ts)
#### api
API-запросы фичи
- Пример кода: [features/api.ts](./ProjectStructExamples.md#features-api-ts)
## shared
Переиспользуемый фундамент проекта.
В shared размещается всё, что не относится к одной конкретной странице или фиче;
### assets
Глобальные ассеты:
- images/ - изображения;
- logo/ - логотип;
- fonts/ - шрифты;
### ui
Базовые UI-компоненты. 
Это универсальные кирпичики интерфейса.
Примеры:
- Button;
- Input;
- Modal;
- Пример кода: [shared/ui.tsx](./ProjectStructExamples.md#shared-ui-tsx)
### types
Общие TypeScript-типы
Примеры: 
- api.ts
    - Пример кода: [shared/types/api.ts](./ProjectStructExamples.md#shared-types-api-ts)
- routes.ts;
    - Пример кода: [shared/types/routes.ts](./ProjectStructExamples.md#shared-types-routes-ts)
### config
Хранит повторно используемые настройки проекта
Помещайте сюда настройки, пути, ключи и конфиги, которые используются повторно.
Примеры:
- routes.ts - строковые path-константы;
- storageKeys.ts
- ui.ts
- Примеры кода: [shared/config.ts](./ProjectStructExamples.md#shared-config-ts)
### constants
Хранит общие неизменяемые константы проекта
Пример: в AppName.ts содержится export const APP_NAME = "Name_Project";
- Пример кода: [shared/constants.ts](./ProjectStructExamples.md#shared-constants-ts)
---

# Краткий "гайд" по организации:
**Это относится ко всему приложению?** -> Тогда app/  
**Это отдельная страница?** -> Тогда pages/  
**Это большой визуальный блок?** -> Тогда widgets/  
**Это действие пользователя?** -> Тогда features/  
**Это что-то общее для разных мест?** -> тогда shared/  
