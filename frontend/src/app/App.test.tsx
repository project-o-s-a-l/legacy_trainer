import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

vi.mock("@/features/AutchContext/AuthContext", () => ({
	useAuth: () => ({
		user: null,
		isAuthenticated: false,
		loading: false,
		refreshAuth: vi.fn(),
		logout: vi.fn(),
	}),
}));

vi.mock("./providers/router/routeConfig", () => ({
	mainPageRoutes: [
		{
			path: "/",
			showNavBar: true,
			showInNavbar: true,
			access: "public",
			element: React.createElement("div", null, "Home Page"),
		},
		{
			path: "/login",
			showNavBar: false,
			showInNavbar: false,
			access: "guest",
			element: React.createElement("div", null, "Login Page"),
		},
		{
			path: "/code",
			showNavBar: true,
			showInNavbar: true,
			access: "private",
			element: React.createElement("div", null, "Code Page"),
		},
	],
}));

vi.mock("./providers/router/renderRoutes", async () => {
	const React = await import("react");
	const { Route } = await import("react-router-dom");

	return {
		renderRoutes: (
			routes: Array<{ path: string; element: React.ReactNode }>,
		) =>
			routes.map((route) =>
				React.createElement(Route, {
					key: route.path,
					path: route.path,
					element: route.element,
				}),
			),
	};
});

vi.mock("@/widgets/index", async () => {
	const React = await import("react");
	const { NavbarContext } = await import("@/shared/lib/layout/NavbarContext");

	const MockNavbar = ({ links }: { links: Array<{ path: string }> }) => {
		const context = React.useContext(NavbarContext);

		return (
			<div data-testid="navbar">
				<div data-testid="navbar-links-count">{links.length}</div>
				<button onClick={context?.toggleNavbar}>toggle navbar</button>
			</div>
		);
	};

	const MockFooter = () => <footer data-testid="footer">Mock Footer</footer>;

	return {
		Navbar: MockNavbar,
		Footer: MockFooter,
	};
});

describe("App", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders Navbar, Footer, and current route content", () => {
		render(
			<MemoryRouter initialEntries={["/"]}>
				<App />
			</MemoryRouter>,
		);

		expect(screen.getByTestId("navbar")).toBeInTheDocument();
		expect(screen.getByTestId("footer")).toBeInTheDocument();
		expect(screen.getByText("Home Page")).toBeInTheDocument();
	});

	it("applies navbar-visible class for route with showNavbar=true", () => {
		const { container } = render(
			<MemoryRouter initialEntries={["/"]}>
				<App />
			</MemoryRouter>,
		);

		const navbarShell = container.querySelector(".navbar-shell");

		expect(navbarShell).toBeInTheDocument();
		expect(navbarShell).toHaveClass("navbar-visible");
		expect(navbarShell).not.toHaveClass("navbar-hidden");
	});

	it("applies navbar-hidden class for route with showNavbar=false", () => {
		const { container } = render(
			<MemoryRouter initialEntries={["/login"]}>
				<App />
			</MemoryRouter>,
		);

		const navbarShell = container.querySelector(".navbar-shell");

		expect(screen.getByText("Login Page")).toBeInTheDocument();
		expect(navbarShell).toBeInTheDocument();
		expect(navbarShell).toHaveClass("navbar-hidden");
		expect(navbarShell).not.toHaveClass("navbar-visible");
	});

	it("passed only routes with showInNavbar=true into Navbar", () => {
		render(
			<MemoryRouter initialEntries={["/"]}>
				<App />
			</MemoryRouter>,
		);

		expect(screen.getByTestId("navbar-links-count")).toHaveTextContent("1");
	});

	it("toggles navbar visibility through NavbarContext", async () => {
		const user = userEvent.setup();

		const { container } = render(
			<MemoryRouter initialEntries={["/"]}>
				<App />
			</MemoryRouter>,
		);

		const navbarShell = container.querySelector(".navbar-shell");
		expect(navbarShell).toHaveClass("navbar-visible");

		await user.click(
			screen.getByRole("button", { name: /toggle navbar/i }),
		);
		expect(navbarShell).toHaveClass("navbar-hidden");

		await user.click(
			screen.getByRole("button", { name: /toggle navbar/i }),
		);
		expect(navbarShell).toHaveClass("navbar-visible");
	});
});
