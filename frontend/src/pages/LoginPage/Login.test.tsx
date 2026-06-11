import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Login from "./Login";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { login_request } from "@/features";
import { MemoryRouter } from "react-router-dom";

const navigateMock = vi.fn();
const refreshAuthMock = vi.fn();

vi.mock("@/features", () => ({
	login_request: vi.fn(),
}));

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
	useAuth: () => ({
		refreshAuth: refreshAuthMock,
	}),
}));

describe("Login", () => {
	beforeEach(() => {
		vi.clearAllMocks();

		vi.mocked(login_request).mockResolvedValue({} as never);
		refreshAuthMock.mockResolvedValue(undefined);
	});

	it("calls login_request with entered email and password", async () => {
		const user = userEvent.setup();

		render(
			<MemoryRouter>
				<Login />
			</MemoryRouter>,
		);

		const emailInput = screen.getByLabelText("Email or username");
		const passwordInput = screen.getByLabelText("Password");
		const submitButton = screen.getByRole("button");

		await user.type(emailInput, "admin@test.com");
		await user.type(passwordInput, "123456");
		await user.click(submitButton);

		await waitFor(() => {
			expect(login_request).toHaveBeenCalledWith(
				"admin@test.com",
				"123456",
			);
			expect(refreshAuthMock).toHaveBeenCalled();
			expect(navigateMock).toHaveBeenCalledWith("/", { replace: true });
		});
	});
});
