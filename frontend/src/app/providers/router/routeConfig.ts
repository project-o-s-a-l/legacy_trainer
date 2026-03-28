import {
	About,
	Contact,
	Possibilites,
	Support,
	Home,
	Login,
} from "@/pages/index";
import type { AppPage } from "@/shared/index.ts";

export const mainPageRoutes: AppPage[] = [
	{
		path: "/about",
		label: "About the company",
		component: About,
		showInNavbar: true,
	},
	{ path: "/", label: "Home", component: Home, showInNavbar: true },
	{
		path: "/possibilites",
		label: "Possibilites",
		component: Possibilites,
		showInNavbar: true,
	},
	{
		path: "/contact",
		label: "Contact",
		component: Contact,
		showInNavbar: true,
	},
	{
		path: "/support",
		label: "Support",
		component: Support,
		showInNavbar: true,
	},
	{ path: "/login", label: "Login", component: Login, showInNavbar: true },
];
