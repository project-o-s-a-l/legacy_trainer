import { ComponentType, } from "react";

export type AppPage = {
    path: string;
    label?: string;
    component: ComponentType;
    showInNavbar?: boolean
};