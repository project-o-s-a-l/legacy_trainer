import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Registration from "./Registration";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { register_request } from "@/features/registr/registr-request.ts";
import { requestRegistrationVerificationCode } from "@/features/verificationCode/verificationCode";
import { MemoryRouter } from "react-router-dom";

const navigateMock = vi.fn();

vi.mock("@/features/registr/registr-request.ts", () => ({
	register_request: vi.fn(),
}));

vi.mock("@/features/verificationCode/verificationCode", () => ({
	requestRegistrationVerificationCode: vi.fn(),
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

describe("Registration", () => {
	beforeEach(() => {
		vi.clearAllMocks();

		vi.mocked(register_request).mockResolvedValue({
			message: "User registered successfully",
			user: {
				id: 1,
				username: "admin",
				email: "admin@test.com",
			},
		});
		vi.mocked(requestRegistrationVerificationCode).mockResolvedValue({
			message: "Verification code sent",
		});
	});

	it("calls registration_request with entered username, email, password, and confirm password", async () => {
		const user = userEvent.setup();

		render(
			<MemoryRouter>
				<Registration />
			</MemoryRouter>,
		);

		const usernameInput = screen.getByPlaceholderText("Enter username");
		const emailInput = screen.getByPlaceholderText("Enter email");
		const passwordInput = screen.getByPlaceholderText("Enter password");
		const confirmPasswordInput = screen.getByPlaceholderText(
			"Confirm your password",
		);
		const submitButton = screen.getByRole("button");

		await user.type(usernameInput, "admin");
		await user.type(emailInput, "admin@test.com");
		await user.type(passwordInput, "123456");
		await user.type(confirmPasswordInput, "123456");
		await user.click(submitButton);

		await waitFor(() => {
			expect(register_request).toHaveBeenCalledWith(
				"admin",
				"admin@test.com",
				"123456",
			);
			expect(requestRegistrationVerificationCode).toHaveBeenCalledWith(
				"admin@test.com",
			);
			expect(navigateMock).toHaveBeenCalledWith("/confirm-email", {
				state: {
					email: "admin@test.com",
					flow: "registration",
				},
			});
		});
	});
});
