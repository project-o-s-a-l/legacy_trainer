import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes } from "react-router-dom";
import { renderRoutes } from "./renderRoutes";
import type { AppPage } from "@/shared/types/routes";

vi.mock("@/widgets/ProtectedRoute/ProtectedRoute", () => ({
	default: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="protected-route">{children}</div>
	),
}));

vi.mock("@/widgets/GuestRoute/GuestRoute", () => ({
	default: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="guest-route">{children}</div>
	),
}));

function PublicPage() {
	return <div>Public page</div>;
}

function PrivatePage() {
	return <div>Private page</div>;
}

function GuestPage() {
	return <div>Guest page</div>;
}

const pages: AppPage[] = [
	{
		path: "/public",
		label: "Public",
		component: PublicPage,
		access: "public",
	},
	{
		path: "/private",
		label: "Private",
		component: PrivatePage,
		access: "private",
	},
	{
		path: "/guest",
		label: "Guest",
		component: GuestPage,
		access: "guest",
	},
];

describe("renderRoutes", () => {
	it("renders public routes without wrappers", () => {
		render(
			<MemoryRouter initialEntries={["/public"]}>
				<Routes>{renderRoutes(pages)}</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByText("Public page")).toBeInTheDocument();
		expect(screen.queryByTestId("protected-route")).not.toBeInTheDocument();
		expect(screen.queryByTestId("guest-route")).not.toBeInTheDocument();
	});

	it("wraps private routes with ProtectedRoute", () => {
		render(
			<MemoryRouter initialEntries={["/private"]}>
				<Routes>{renderRoutes(pages)}</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByTestId("protected-route")).toBeInTheDocument();
		expect(screen.getByText("Private page")).toBeInTheDocument();
	});

	it("wraps guest routes with GuestRoute", () => {
		render(
			<MemoryRouter initialEntries={["/guest"]}>
				<Routes>{renderRoutes(pages)}</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByTestId("guest-route")).toBeInTheDocument();
		expect(screen.getByText("Guest page")).toBeInTheDocument();
	});
});
