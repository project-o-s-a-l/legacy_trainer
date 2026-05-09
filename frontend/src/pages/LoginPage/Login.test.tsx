import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Login from "./Login";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { login_request } from "@/features";

const navigateMock = vi.fn();
const refreshAuthMock = vi.fn();

vi.mock("@/features", () => ({
	login_request: vi.fn(),
}));

vi.mock("react-router-dom", () => ({
	useNavigate: () => navigateMock,
}));

vi.mock("@/features/AutchContext/AuthContext", () => ({
	useAuth: () => ({
		refreshAuth: refreshAuthMock,
	}),
}));

describe("Login", () => {
	beforeEach(() => {
		vi.clearAllMocks();

		vi.mocked(login_request).mockResolvedValue({} as any);

		refreshAuthMock.mockResolvedValue(undefined);
	});

	it("calls login_request with entered email and password", async () => {
		const user = userEvent.setup();

		render(<Login />);

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
		});
	});
});