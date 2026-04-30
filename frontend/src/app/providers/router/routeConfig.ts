import { CodeBlock } from "@/pages/CodeBlockPage/CodeBlock";
import {
	About,
	Contact,
	Possibilites,
	Support,
	Home,
	Login,
	Registration,
	CodePage,
	CodeEditor,
	ChooseTask,
	Profile,
	SolutionResult,
} from "@/pages/index";

import { ProfileImg } from "@/shared/index.ts";
import type { AppPage } from "@/shared/index.ts";

export const mainPageRoutes: AppPage[] = [
	{
		path: "/about",
		label: "About the company",
		component: About,
		showInNavbar: true,
		access: "public",
	},
	{
		path: "/",
		label: "Home",
		component: Home,
		showInNavbar: true,
		access: "public",
	},
	{
		path: "/possibilites",
		label: "Possibilites",
		component: Possibilites,
		showInNavbar: true,
		access: "public",
	},
	{
		path: "/contact",
		label: "Contact",
		component: Contact,
		showInNavbar: true,
		access: "public",
	},
	{
		path: "/support",
		label: "Support",
		component: Support,
		showInNavbar: true,
		access: "public",
	},
	{
		path: "/login",
		label: "Login",
		component: Login,
		showInNavbar: true,
		access: "guest",
	},
	{
		path: "/Registration",
		label: "Registration",
		component: Registration,
		showInNavbar: true,
		access: "guest",
	},
	{
		path: "/CodePage",
		label: "CodePage",
		component: CodePage,
		showInNavbar: false,
		access: "private"
	},
	{
		path: "/CodeBlock",
		label: "CodeBlock",
		component: CodeEditor,
		showInNavbar: true,
		access: "public"
	},
	{
		path: "/ChooseTask",
		label: "ChooseTask",
		component: ChooseTask,
		showInNavbar: true,
		access: "private"
	},
	{
		path: "/profile",
		label: "Profile",
		component: Profile,
		showInNavbar: true,
		access: "private"
	},
	{
		path: "/result",
		label: "Solution Result",
		component: SolutionResult,
		showInNavbar: true,
		access: "public"
	}
];
