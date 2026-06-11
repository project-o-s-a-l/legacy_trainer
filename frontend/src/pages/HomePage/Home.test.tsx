import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Home from "./Home";

const navigateMock = vi.fn();
const useAuthMock = vi.fn();

vi.mock("react-router-dom", async () => {
	const actual =
		await vi.importActual<typeof import("react-router-dom")>(
			"react-router-dom",
		);

	return {
		...actual,
		useNavigate: () => navigateMock,
	};
});

vi.mock("@/features/AutchContext/useAuth", () => ({
	useAuth: () => useAuthMock(),
}));

describe("Home", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders a loading state while auth is being resolved", () => {
		useAuthMock.mockReturnValue({
			isAuthenticated: false,
			loading: true,
		});

		render(
			<MemoryRouter>
				<Home />
			</MemoryRouter>,
		);

		expect(screen.getByText("Loading...")).toBeInTheDocument();
	});

	it("shows guest actions and navigates to registration and login", async () => {
		const user = userEvent.setup();

		useAuthMock.mockReturnValue({
			isAuthenticated: false,
			loading: false,
		});

		render(
			<MemoryRouter>
				<Home />
			</MemoryRouter>,
		);

		await user.click(screen.getByRole("button", { name: "Registration" }));
		await user.click(screen.getByRole("button", { name: "Sign In" }));

		expect(navigateMock).toHaveBeenNthCalledWith(1, "/Registration");
		expect(navigateMock).toHaveBeenNthCalledWith(2, "/login");
	});

	it("shows member actions and navigates to profile and task selection", async () => {
		const user = userEvent.setup();

		useAuthMock.mockReturnValue({
			isAuthenticated: true,
			loading: false,
		});

		render(
			<MemoryRouter>
				<Home />
			</MemoryRouter>,
		);

		await user.click(screen.getByRole("button", { name: "Profile" }));
		await user.click(screen.getByRole("button", { name: "Generate Task" }));

		expect(navigateMock).toHaveBeenNthCalledWith(1, "/profile");
		expect(navigateMock).toHaveBeenNthCalledWith(2, "/ChooseTask");
	});
});
