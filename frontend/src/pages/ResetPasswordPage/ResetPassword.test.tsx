import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import ResetPassword from "./ResetPassword";
import { completePasswordRecoveryReset } from "@/features/verificationCode/verificationCode";

type MockLocationState = {
	email?: string;
	resetToken?: string;
} | null;

const { navigateMock, mockLocationState } = vi.hoisted(() => ({
	navigateMock: vi.fn(),
	mockLocationState: { current: null as MockLocationState },
}));

vi.mock("@/features/verificationCode/verificationCode", () => ({
	completePasswordRecoveryReset: vi.fn(),
}));

vi.mock("react-router-dom", async () => {
	const actual =
		await vi.importActual<typeof import("react-router-dom")>(
			"react-router-dom",
		);

	return {
		...actual,
		useNavigate: () => navigateMock,
		useLocation: () => ({
			state: mockLocationState.current,
		}),
	};
});

function renderPage() {
	return render(
		<MemoryRouter>
			<ResetPassword />
		</MemoryRouter>,
	);
}

describe("ResetPassword", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mockLocationState.current = {
			email: "restore@test.com",
			resetToken: "reset-token",
		};

		vi.mocked(completePasswordRecoveryReset).mockResolvedValue({
			message: "Password updated",
		});
	});

	it("submits a new password and redirects to login", async () => {
		const user = userEvent.setup();

		renderPage();

		await user.type(screen.getByLabelText("New password"), "secret123");
		await user.type(
			screen.getByLabelText("Confirm new password"),
			"secret123",
		);
		await user.click(screen.getByRole("button", { name: "Save password" }));

		await waitFor(() => {
			expect(completePasswordRecoveryReset).toHaveBeenCalledWith(
				"restore@test.com",
				"secret123",
				"secret123",
				"reset-token",
			);
			expect(navigateMock).toHaveBeenCalledWith("/login", {
				replace: true,
				state: {
					notice: "Password updated",
				},
			});
		});
	});

	it("shows an error when the reset request fails", async () => {
		const user = userEvent.setup();

		vi.mocked(completePasswordRecoveryReset).mockRejectedValue(
			new Error("Unable to update password"),
		);

		renderPage();

		await user.type(screen.getByLabelText("New password"), "secret123");
		await user.type(
			screen.getByLabelText("Confirm new password"),
			"secret123",
		);
		await user.click(screen.getByRole("button", { name: "Save password" }));

		expect(
			await screen.findByText("Unable to update password"),
		).toBeInTheDocument();
		expect(navigateMock).not.toHaveBeenCalled();
	});

	it("disables the form when the page is opened without recovery state", () => {
		mockLocationState.current = null;

		renderPage();

		expect(screen.getByLabelText("New password")).toBeDisabled();
		expect(screen.getByLabelText("Confirm new password")).toBeDisabled();
		expect(
			screen.getByRole("button", { name: "Save password" }),
		).toBeDisabled();
	});
});
