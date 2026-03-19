import type { ComponentType } from "react";
import About from "../../../pages/AboutPage/About";
import Contact from "../../../pages/ContactPage/Contact";
import Possibilites from "../../../pages/PossibilitesPage/Possibilites";
import Support from "../../../pages/SupportPage/Support";
import Sing_in from "../../../pages/SingInPage/SingIn";
import Home from "../../../pages/HomePage/Home";
import type { AppPage } from "../../../shared/types/routes"



export const mainPageRoutes: AppPage[] = [
    {path: "/about", label: "About the company", component: About, showInNavbar: true },
    {path: "/", label: "Home", component: Home, showInNavbar: true },
    {path: "/possibilites", label: "Possibilites", component: Possibilites, showInNavbar: true },
    {path: "/contact", label: "Contact", component: Contact, showInNavbar: true },
    {path: "/support", label: "Support", component: Support, showInNavbar: true },
    {path: "/sing_in", label: "Sing in", component: Sing_in, showInNavbar: true },
]

