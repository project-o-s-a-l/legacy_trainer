import React from "react";
import { Route } from "react-router-dom";
import type { AppPage } from "../../../shared/types/routes"


export function renderRoutes(pages: AppPage[]) {
    return pages.map(({ path, component: Component})=> (
        <Route key={path} path={path} element={<Component/>}/>
    ))
}