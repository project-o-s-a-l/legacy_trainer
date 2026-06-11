import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import ForgotPassword from "./ForgotPassword";
import { requestPasswordRecoveryCode } from "@/features/verificationCode/verificationCode";

const navigateMock = vi.fn();

vi.mock("@/features/verificationCode/verificationCode", () => ({
	requestPasswordRecoveryCode: vi.fn(),
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

describe("ForgotPassword", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.mocked(requestPasswordRecoveryCode).mockResolvedValue({
			message: "Verification code sent",
		});
	});

	it("requests a recovery code and navigates to the verification page", async () => {
		const user = userEvent.setup();

		render(
			<MemoryRouter>
				<ForgotPassword />
			</MemoryRouter>,
		);

		await user.type(
			screen.getByLabelText("Email"),
			"  recovery@test.com  ",
		);
		await user.click(screen.getByRole("button", { name: "Send code" }));

		await waitFor(() => {
			expect(requestPasswordRecoveryCode).toHaveBeenCalledWith(
				"recovery@test.com",
			);
			expect(navigateMock).toHaveBeenCalledWith("/confirm-email", {
				state: {
					email: "recovery@test.com",
					flow: "recovery",
				},
			});
		});
	});

	it("shows an error message when the recovery request fails", async () => {
		const user = userEvent.setup();

		vi.mocked(requestPasswordRecoveryCode).mockRejectedValue(
			new Error("Recovery request failed"),
		);

		render(
			<MemoryRouter>
				<ForgotPassword />
			</MemoryRouter>,
		);

		await user.type(screen.getByLabelText("Email"), "recovery@test.com");
		await user.click(screen.getByRole("button", { name: "Send code" }));

		expect(
			await screen.findByText("Recovery request failed"),
		).toBeInTheDocument();
		expect(navigateMock).not.toHaveBeenCalled();
	});
});
