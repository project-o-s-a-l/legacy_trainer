# index-ts
```TypeScript
export { default } from "./Navbar";
```
Использование:
```TypeScript
import Navbar from "../widgets/Navbar";
```
В index.ts может быть так же несколько импоротов:
```TypeScript
export { default as LoginForm } from "./ui/LoginForm";
export { default as SignOutButton  } from "./ui/SignOutButton";
export { useAuth } from "./model/useAuth";
```
Использование:
```TypeScript
import { LoginForm, useAuth } from "../features/auth";
```

# app-tsx
```TypeScript
import React from 'react';
import './App.css';
import Navbar from '../widgets/Navbar/Navbar';
import { Route, Routes } from 'react-router';
import { mainPageRoutes } from './providers/router/routeConfig';
import { renderRoutes } from './providers/router/renderRoutes';
import Footer from '../widgets/Footer/Footer';



function App() {
  return (
    <div className="App">
     <Navbar links={mainPageRoutes}/>
     <Routes>
      {renderRoutes(mainPageRoutes)}
     </Routes>
    <Footer></Footer>     
    </div>
  );
}

export default App;
```

# routeConfig-ts
```TypeScript
import About from "../../../pages/AboutPage/About";
import Sing_in from "../../../pages/SingInPage/Sing_in";
import Home from "../../../pages/HomePage/Home";
import type { AppPage } from "../../../shared/types/routres"

export const mainPageRoutes: AppPage[] = [
    {path: "/about", label: "About the company", component: About, showInNavbar: true },
    {path: "/", label: "Home", component: Home, showInNavbar: true },
    {path: "/sing_in", label: "Sing in", component: Sing_in, showInNavbar: true },
]
```

# renderRoutes-tsx
```TypeScript
import React from "react";
import { Route } from "react-router-dom";
import type { AppPage } from "../../../shared/types/routres"


export function renderRoutes(pages: AppPage[]) {
    return pages.map(({ path, component: Component})=> (
        <Route key={path} path={path} element={<Component/>}/>
    ))
}
```

# globalCSS:
```CSS
@import "./variables.css";
@import "./typography.css";

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}
```

# variableCSS:
```CSS
:root {
  --color-bg: #ffffff;
  --color-text: #111111;
  --container-width: 1200px;
  --radius-md: 12px;
}
```

# env-ts
```TypeScript
export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:3001";
```

# constants-ts
```TypeScript
export const APP_NAME = "LegacyTrainer";
```

# pages-tsx
```TypeScript
export default function HomePage() {
  return (
    <main>
      <h1>LegacyTrainer</h1>
      <p>Главная страница проекта</p>
    </main>
  );
}
```

# widgets-tsx
### NavBar:
```TypeScript
import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav>
      <NavLink to="/">Home</NavLink>
      <NavLink to="/about">About</NavLink>
      <NavLink to="/contact">Contact</NavLink>
    </nav>
  );
}
```
### Footer:
```TypeScript
export default function Footer() {
  return (
    <footer>
      <p>&copy; 2026 LegacyTrainer</p>
    </footer>
  );
}
```

# features-ui-tsx
```TypeScript
export default function LoginForm() {
  return (
    <form>
      <input type="email" placeholder="Email" />
      <input type="password" placeholder="Password" />
      <button type="submit">Sign in</button>
    </form>
  );
}
```

# features-model-ts
```TypeScript
export function useAuth() {
  const isAuth = false;

  return { isAuth };
}
```

# features-api-ts
```TypeScript
export async function login(email: string, password: string) {
  return fetch("/api/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}
```

# shared-ui-tsx
```TypeScript
type ButtonProps = {
  children: React.ReactNode;
};

export default function Button({ children }: ButtonProps) {
  return <button>{children}</button>;
}
```

# shared-types-api-ts
```TypeScript
export type ApiResponse<T> = {
  data: T;
  success: boolean;
};
```

# shared-types-routes-ts
```TypeScript
import { ComponentType, } from "react";

export type AppPage = {
    path: string;
    label?: string;
    component: ComponentType;
    showInNavbar?: boolean
};
```

# shared-config-ts
### routes:
```TypeScript
export const ROUTES = {
  HOME: "/",
  ABOUT: "/about",
  CONTACT: "/contact",
};
```
### storageKeys:
```TypeScript
export const STORAGE_KEYS = {
  THEME: "theme",
  TOKEN: "token",
};
```

# shared-constants-ts
```TypeScript
export const STORAGE_KEYS = {
  THEME: "theme",
  TOKEN: "token",
};
```