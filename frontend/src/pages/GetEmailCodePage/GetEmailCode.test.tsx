import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import CodePage from "./GetEmailCode";
import {
	confirmPasswordRecoveryCode,
	confirmRegistrationVerificationCode,
	requestPasswordRecoveryCode,
	requestRegistrationVerificationCode,
} from "@/features/verificationCode/verificationCode";

type MockLocationState = {
	email?: string;
	flow?: "registration" | "recovery";
} | null;

const { navigateMock, mockLocationState } = vi.hoisted(() => ({
	navigateMock: vi.fn(),
	mockLocationState: { current: null as MockLocationState },
}));

vi.mock("@/features/verificationCode/verificationCode", () => ({
	confirmPasswordRecoveryCode: vi.fn(),
	confirmRegistrationVerificationCode: vi.fn(),
	requestPasswordRecoveryCode: vi.fn(),
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
		useLocation: () => ({
			state: mockLocationState.current,
		}),
	};
});

function renderPage() {
	return render(
		<MemoryRouter>
			<CodePage />
		</MemoryRouter>,
	);
}

describe("GetEmailCode", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mockLocationState.current = {
			email: "user@test.com",
			flow: "registration",
		};

		vi.mocked(confirmRegistrationVerificationCode).mockResolvedValue({
			message: "Registration completed",
		});
		vi.mocked(confirmPasswordRecoveryCode).mockResolvedValue({
			message: "Recovery confirmed",
			resetToken: "reset-token",
		});
		vi.mocked(requestRegistrationVerificationCode).mockResolvedValue({
			message: "New registration code sent",
		});
		vi.mocked(requestPasswordRecoveryCode).mockResolvedValue({
			message: "New recovery code sent",
		});
	});

	it("submits a registration verification code and redirects to login", async () => {
		const user = userEvent.setup();

		renderPage();

		await user.type(screen.getByLabelText("Verification code"), "123456");
		await user.click(screen.getByRole("button", { name: "Next" }));

		await waitFor(() => {
			expect(confirmRegistrationVerificationCode).toHaveBeenCalledWith(
				"user@test.com",
				"123456",
			);
			expect(navigateMock).toHaveBeenCalledWith("/login", {
				replace: true,
				state: {
					notice: "Registration completed",
				},
			});
		});
	});

	it("submits a recovery verification code and redirects to reset password", async () => {
		const user = userEvent.setup();

		mockLocationState.current = {
			email: "restore@test.com",
			flow: "recovery",
		};

		renderPage();

		await user.type(screen.getByLabelText("Verification code"), "654321");
		await user.click(screen.getByRole("button", { name: "Next" }));

		await waitFor(() => {
			expect(confirmPasswordRecoveryCode).toHaveBeenCalledWith(
				"restore@test.com",
				"654321",
			);
			expect(navigateMock).toHaveBeenCalledWith("/reset-password", {
				replace: true,
				state: {
					email: "restore@test.com",
					resetToken: "reset-token",
				},
			});
		});
	});

	it("resends a code for the recovery flow and shows a status message", async () => {
		const user = userEvent.setup();

		mockLocationState.current = {
			email: "restore@test.com",
			flow: "recovery",
		};

		renderPage();

		await user.click(screen.getByRole("button", { name: "Resend it" }));

		await waitFor(() => {
			expect(requestPasswordRecoveryCode).toHaveBeenCalledWith(
				"restore@test.com",
			);
		});

		expect(
			await screen.findByText("New recovery code sent"),
		).toBeInTheDocument();
	});

	it("shows a helpful state when opened without location data", () => {
		mockLocationState.current = null;

		renderPage();

		expect(
			screen.getByText(
				"Email is unavailable. Restart the flow from the previous screen.",
			),
		).toBeInTheDocument();
		expect(screen.getByLabelText("Verification code")).toBeDisabled();
		expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
		expect(
			screen.getByRole("button", { name: "Resend it" }),
		).toBeDisabled();
	});

	it("renders recovery-specific copy and back link", () => {
		mockLocationState.current = {
			email: "restore@test.com",
			flow: "recovery",
		};

		renderPage();

		expect(screen.getByText("Password recovery")).toBeInTheDocument();
		expect(
			screen.getByText(
				"Enter the verification code to continue recovering access to your account.",
			),
		).toBeInTheDocument();
		expect(screen.getByRole("link", { name: "Back" })).toHaveAttribute(
			"href",
			"/forgot-password",
		);
	});
});
