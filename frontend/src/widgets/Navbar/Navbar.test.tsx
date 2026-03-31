import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import Navbar from "./Navbar";
import type { AppPage } from "@/shared/types";

vi.mock("../../shared/assets/logo/logo.png", () => ({
	default: "mocked-logo.png",
}));

const MockComponent = () => <div>Mock Component</div>;

const createLinks = (): AppPage[] => [
	{
		path: "/",
		label: "Home",
		component: MockComponent,
		showInNavbar: true,
	},
	{
		path: "/about",
		label: "About the company",
		component: MockComponent,
		showInNavbar: true,
	},
	{
		path: "/contact",
		label: "Contact",
		component: MockComponent,
		showInNavbar: true,
	},
	{
		path: "/hidden",
		label: "Hidden page",
		component: MockComponent,
		showInNavbar: false,
	},
];

const renderNavbar = (links: AppPage[]) => {
	return render(
		<MemoryRouter>
			<Navbar links={links} />
		</MemoryRouter>,
	);
};

describe("Navbar", () => {
	it("renders project name and logo", () => {
		renderNavbar(createLinks());

		expect(screen.getByText("LegacyTrainer")).toBeInTheDocument();
		expect(screen.getByAltText("logo Project O.S.A.L")).toBeInTheDocument();
	});
	it("renders only links with showInNavbar=true", () => {
		renderNavbar(createLinks());

		expect(screen.getByText("Home")).toBeInTheDocument();
		expect(screen.getByText("About the company")).toBeInTheDocument();
		expect(screen.getByText("Contact")).toBeInTheDocument();
		expect(screen.queryByText("Hidden page")).not.toBeInTheDocument();
	});

	it("renders correct href attributes for visible links", () => {
		renderNavbar(createLinks());

		expect(screen.getByRole("link", { name: "Home" })).toHaveAttribute(
			"href",
			"/",
		);

		expect(
			screen.getByRole("link", { name: "About the company" }),
		).toHaveAttribute("href", "/about");

		expect(screen.getByRole("link", { name: "Contact" })).toHaveAttribute(
			"href",
			"/contact",
		);
	});

	it("renders no navigation links when links array is empty", () => {
		renderNavbar([]);

		expect(screen.queryByRole("link")).not.toBeInTheDocument();
		expect(screen.getByAltText("logo Project O.S.A.L")).toBeInTheDocument();

		expect(screen.getByText("LegacyTrainer")).toBeInTheDocument();
	});

	it("renders the exact number of visible links", () => {
		const links = createLinks();
		renderNavbar(links);

		const visibleLinks = links.filter((link) => link.showInNavbar).length;
		const renderedLinks = screen.getAllByRole("link");

		expect(renderedLinks).toHaveLength(visibleLinks);
	});
});
