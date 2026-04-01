import React, { useEffect, useMemo, useState } from "react";
import "./App.css";
import { Navbar } from "@/widgets/index";
import { Routes, useLocation } from "react-router-dom";
import { mainPageRoutes } from "./providers/router/routeConfig";
import { renderRoutes } from "./providers/router/renderRoutes";
import { Footer } from "@/widgets/index";
import { NavbarContext } from "@/shared/lib/layout/NavbarContext";

function App() {
	const location = useLocation();
	const currentRoute = mainPageRoutes.find(
		(route) => route.path === location.pathname,
	);

	const defaultNavbarVisible = currentRoute?.showNavBar ?? true;

	const [isNavbarVisible, setNavbarVisible] = useState(defaultNavbarVisible);

	useEffect(() => {
		setNavbarVisible(defaultNavbarVisible);
	}, [defaultNavbarVisible, location.pathname]);

	const toggleNavbar = () => {
		setNavbarVisible((prev) => !prev);
	};

	const navbarConetxtValue = useMemo(
		() => ({
			isNavbarVisible,
			setNavbarVisible,
			toggleNavbar,
		}),
		[isNavbarVisible],
	);

	return (
		<NavbarContext.Provider value={navbarConetxtValue}>
			<div className="App">
				<div className={`navbar-shell ${isNavbarVisible ? "navbar-visible" : "navbar-hidden"}`}>
					<Navbar links={mainPageRoutes.filter((route) => route.showInNavbar)} />
					{/* {isNavbarVisible && <Navbar links={mainPageRoutes.filter((route) => route.showInNavbar)} />} */}
				</div>
				{/* <Navbar links={mainPageRoutes}/> */}
				<Routes>{renderRoutes(mainPageRoutes)}</Routes>
				<Footer></Footer>
			</div>
		</NavbarContext.Provider>
	);
}

export default App;
