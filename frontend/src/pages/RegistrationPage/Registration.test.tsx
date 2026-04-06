import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Registration from "./Registration";
import { describe, expect, it, vi } from "vitest";
import { register_request } from "@/features/registr/registr-request.ts";

vi.mock("@/features/registr/registr-request.ts", () => ({
	register_request: vi.fn(),
}));

describe("Registration", () => {
	it("calls registration_request with entered username, email, password, and confirm password", async () => {
		const user = userEvent.setup();
		render(<Registration />);

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

		expect(register_request).toHaveBeenCalledWith(
			"admin",
			"admin@test.com",
			"123456",
		);
	});
});
