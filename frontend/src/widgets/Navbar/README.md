# Документация по использованию 'Navbar'
Для начала нужно импортировать сам Navbar из директории widgets/Navbar:
```TypeScript
import Navbar from 'path/to/navbar';
```
Затем нужно импортировать пути, к примеру мы находимся на странице с профилем, тогда в директории /app/providers/router/ и в файле routeConfig.ts, нам нужно экспортировать массив с путями:
```TypeScript
// Здесь должны быть импорты компонентов из директории pages/.../
import type { AppPage } from "path/to/types/routes"

export const profilePageRoutes: AppPage[] = [
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
Это импорт типов для типизации массива
## Типы массива:
```TypeScript
import { ComponentType, } from "react";

export type AppPage = {
    path: string;
    label: string;
    component: ComponentType;
    showInNavbar?: boolean
};
```

Возвращаемся к файлу куда мы собрались добавить Navbar. Теперь мы должны импортировать наш массив в этот файл:
```TypeScript
import { profilePageRoutes } from "path/to/providers/router/routeConfig";
```
После этого необходимо подключить renderRoutes, для генерации маршрутизации:
```TypeScript
import { renderRoutes } from 'path/to/providers/router/renderRoutes';
```

### Основная часть кода(разметка+ts код):
```TypeScript
import { Routes } from "react-router-dom";
import Navbar from "path/to/navbar";
import { profilePageRoutes } from "path/to/providers/router/routeConfig";
import { renderRoutes } from "path/to/providers/router/renderRoutes";

function Profile() {
  return (
    <div className="ProfilePage">
     <Navbar links={profilePageRoutes}/>
     <Routes>
      {renderRoutes(profilePageRoutes)}
     </Routes>
    </div>
  );
}
export default Profile;
```


`<Navbar links={profilePageRoutes}/>` - здесь мы подключаем ссылки к нашему Navbar

`<Routes></Routes>` - компонент из react-router-dom для работы с маршрутизацией

### Внутренняя работа
В этом блоке описана внутренняя работа некоторых компонентов Navbar
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
- `links` - это массив передаваемых ссылок а `link` - конкретная ссылка;
- `links.filter((link) => link.showInNavbar)` - фильрует по принципу link.showInNavbar === true;
- `map(link => (TSX-code))` - превращает каждый элемент в TSX-код;
- `<NavLink></NavLink>` - компонент из react-router-dom, используется для навигации;
    - `key={link.path}` - key специальный React-prop для уникальной идентификации элементов списка. Используется path, т.к. адрес страниц должен быть уникальным;
    - `to={link.path}` - по какому адресу идет маршрутизация;
    - `{link.label}` - отображаемый текст;

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
- `pages.map(({path, component: Component}) => (TSX-Code))` - Берем массив из AppPage и преобразуем его в TSX-код;
- `<Route/>` - компонент из react-router-dom, используется для описания маршрута;
    - `element={<Component/>}` - какой компонент нужно отобразить пользователю;
    - Остальные компоненты разобраны выше [NavLink](#links-rendering)
# ВАЖНО
Набор ссылок в Navbar может зависеть от состояния пользователя.
Например, для неавторизованного пользователя можно показывать ссылки Sign in и Register, а для авторизованного — Profile и Logout.
Для этого можно передавать в Navbar другой массив маршрутов или предварительно фильтровать ссылки перед передачей в компонент.
