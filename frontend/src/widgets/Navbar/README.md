# Документация по использованию 'Navbar'
В этом проекте Navbar получает не отдельный список ссылок, а общий массив маршрутов приложения через props.  
Благодаря этому приложение может показывать разную навигацию в зависимости от состояния пользователя.  
Например, для гостя можно передать guestRoutes, а для авторизованного пользователя — authRoutes.  
Для начала нужно импортировать сам Navbar из директории widgets/Navbar:
```TypeScript
import Navbar from 'path/to/navbar';
```
Если в приложении есть отдельный layout для авторизованного пользователя, в него можно передать массив authRoutes.
Этот массив можно описать в файле routeConfig.ts внутри директории /app/providers/router/.
В каждом объекте массива хранится путь, текст ссылки, компонент страницы и флаг отображения в Navbar:
```TypeScript
// Здесь должны быть импорты компонентов из директории pages/.../
import type { AppPage } from "path/to/types/routes"

export const authRoutes: AppPage[] = [
    {path: "/about", label: "About the company", component: About, showInNavbar: true },
    {path: "/", label: "Home", component: Home, showInNavbar: true },
    {path: "/possibilities", label: "Possibilities", component: Possibilities, showInNavbar: true },
    {path: "/contact", label: "Contact", component: Contact, showInNavbar: true },
    {path: "/support", label: "Support", component: Support, showInNavbar: true },
    {path: "/profile", label: "Profile", component: Profile, showInNavbar: true}
]
```
Также отмечу:
```TypeScript
 import type { AppPage } from "path/to/types/routes"  
```
Тип AppPage задаёт структуру объекта маршрута: путь, текст ссылки, компонент страницы и флаг отображения в Navbar
## Тип AppPage:
```TypeScript
import { ComponentType } from "react";

export type AppPage = {
    path: string;
    label: string;
    component: ComponentType;
    showInNavbar?: boolean
};
```

Возвращаемся к файлу куда мы собрались добавить Navbar. Теперь мы должны импортировать наш массив в этот файл:
```TypeScript
import { authRoutes } from "path/to/providers/router/routeConfig";
```
Затем импортируйте renderRoutes. Эта функция преобразует массив конфигураций в набор компонентов Route:
```TypeScript
import { renderRoutes } from 'path/to/providers/router/renderRoutes';
```

### Основная часть кода(TSX):
```TypeScript
import { Routes } from "react-router-dom";
import Navbar from "path/to/navbar";
import { authRoutes } from "path/to/providers/router/routeConfig";
import { renderRoutes } from "path/to/providers/router/renderRoutes";

function AuthorizedLayout() {
  return (
    <div className="AuthorizedPage">
     <Navbar links={authRoutes}/>
     <Routes>
      {renderRoutes(authRoutes)}
     </Routes>
    </div>
  );
}
export default AuthorizedLayout;
```


- Navbar не хранит ссылки внутри себя. Вместо этого компонент получает массив маршрутов через prop links. Это позволяет использовать один и тот же компонент Navbar на разных страницах с разным набором ссылок:
    ```TypeScript
    <Navbar links={authRoutes}/>
    ```
- Routes — это контейнер для компонентов Route.
React Router сравнивает текущий URL с маршрутами внутри Routes и отображает подходящий компонент:

    ```TypeScript
    <Routes></Routes>
    ```
## Итого
После подключения Navbar происходит следующее:
- Navbar покажет только те ссылки, у которых showInNavbar: true;
- renderRoutes создаст маршруты для всех объектов массива;
- При смене массива можно изменить навигацию для гостя и авторизованного пользователя;

### Внутренняя работа
Ниже показано, как Navbar рендерит ссылки и как функция renderRoutes создаёт маршруты из конфигурации
#### links-rendering:
```TypeScript
<div className="nav-links">
    {links
        .filter((link) => link.showInNavbar)
        .map(link => (
            <NavLink key={link.path} className="navlink" to={link.path}> 
                {link.label}
            </NavLink>
    ))}
</div>
```

- фильрует по принципу link.showInNavbar === true:
    ```TypeScript
    links.filter((link) => link.showInNavbar)
    ```
- превращает каждый элемент в TSX-код:
    ```TypeScript
    map((link) => (
        ...
    ))
    ```
- компонент из react-router-dom, используется для навигации:
    ```TypeScript
    <NavLink></NavLink>
    ```
    - key специальный React-prop для уникальной идентификации элементов списка. Используется path, т.к. адрес страниц должен быть уникальным:
        ```TypeScript
        key={link.path}
        ```
    - по какому адресу идет маршрутизация:
        ```TypeScript
        to={link.path}
        ```
    - отображаемый текст:
        ```TypeScript
        {link.label}
        ```

#### Как реализован renderRoutes:
```TypeScript
import { Route } from "react-router-dom";
import type { AppPage } from "../../../shared/types/routes"


export function renderRoutes(pages: AppPage[]) {
    return pages.map(({ path, component: Component})=> (
        <Route key={path} path={path} element={<Component/>}/>
    ))
}
```
- Берем массив из AppPage и преобразуем его в TSX-код:
    ```TypeScript
    pages.map(({path, component: Component}) => (...))
    ```
- компонент из react-router-dom, используется для описания маршрута:
    ```TypeScript
    <Route/>
    ```
    - какой компонент нужно отобразить пользователю:
        ```TypeScript
        element={<Component/>}
        ```
    - Остальные компоненты разобраны выше [NavLink](#links-rendering)
# ВАЖНО
Набор ссылок в Navbar может зависеть от состояния пользователя.
Например, для неавторизованного пользователя можно показывать ссылки Sign in и Register, а для авторизованного — Profile и Logout.
Для этого можно передавать в Navbar другой массив конфигураций маршрутов или предварительно фильтровать ссылки перед передачей в компонент.
