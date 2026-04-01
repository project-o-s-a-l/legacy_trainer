import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Login from "./Login";
import { describe, expect, it, vi } from "vitest";
import { login_request } from "@/features";

vi.mock("@/features", () => ({
	login_request: vi.fn(),
}));

describe("Login", () => {
	it("calls login_request with entered email and password", async () => {
		const user = userEvent.setup();
		render(<Login />);

		const emailInput = screen.getByPlaceholderText("Enter your email");
		const passwordInput = screen.getByPlaceholderText(
			"Enter your password",
		);
		const submitButton = screen.getByRole("button");

		await user.type(emailInput, "admin@test.com");
		await user.type(passwordInput, "123456");
		await user.click(submitButton);

		expect(login_request).toHaveBeenCalledWith("admin@test.com", "123456");
	});
});
