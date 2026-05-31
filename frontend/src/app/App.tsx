import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { Navbar } from "@/widgets/index";
import { Routes, useLocation, useNavigate } from "react-router-dom";
import { mainPageRoutes } from "./providers/router/routeConfig";
import { renderRoutes } from "./providers/router/renderRoutes";
import { Footer } from "@/widgets/index";
import { NavbarContext } from "@/shared/index.ts";
import "./styles/variables.css";
import { useAuth } from "@/features/AutchContext/AuthContext";

function App() {
	const location = useLocation();
	const navigate = useNavigate();
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
	const { isAuthenticated, loading, logout } = useAuth();

	if (loading) {
		return <div className="app-loading">Loading...</div>;
	}

	const navBarLinks = mainPageRoutes.filter((route) => {
		if (!route.showInNavbar) return false;

		if (route.access === "public") return true;
		if (route.access === "private") return isAuthenticated;
		if (route.access === "guest") return !isAuthenticated;

		return false;
	});

	const handleLogout = async () => {
		await logout();
		navigate("/", { replace: true });
	};

	return (
		<NavbarContext.Provider value={navbarConetxtValue}>
			<div className="App">
				<div
					className={`navbar-shell ${isNavbarVisible ? "navbar-visible" : "navbar-hidden"}`}
				>
					<Navbar
						links={navBarLinks.filter(
							(route) => route.showInNavbar,
						)}
						isAuthenticated={isAuthenticated}
						onLogout={() => {
							void handleLogout();
						}}
					/>
				</div>
				<div className="app-content">
					<div className="app-route">
						<Routes>{renderRoutes(mainPageRoutes)}</Routes>
					</div>
				</div>
				<Footer />
			</div>
		</NavbarContext.Provider>
	);
}

export default App;
