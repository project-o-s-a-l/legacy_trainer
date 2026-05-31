import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	completePasswordRecoveryReset,
	confirmPasswordRecoveryCode,
	confirmRegistrationVerificationCode,
	requestPasswordRecoveryCode,
	requestRegistrationVerificationCode,
} from "./verificationCode";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

describe("verificationCode", () => {
	beforeEach(() => {
		vi.restoreAllMocks();
		vi.stubGlobal("fetch", vi.fn());
	});

	it("requests a registration verification code through the backend api", async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response(JSON.stringify({ message: "Code sent" }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			}),
		);

		const result = await requestRegistrationVerificationCode("User@Test.com");

		expect(fetch).toHaveBeenCalledWith(
			"http://localhost:8080/api/v1/auth/request-verification-code",
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({
					email: "user@test.com",
					flow: "registration",
				}),
			}),
		);
		expect(result.message).toBe("Code sent");
	});

	it("requests a recovery verification code through the backend api", async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response(JSON.stringify({ message: "Recovery code sent" }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			}),
		);

		const result = await requestPasswordRecoveryCode("user@test.com");

		expect(fetch).toHaveBeenCalledWith(
			"http://localhost:8080/api/v1/auth/request-verification-code",
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({
					email: "user@test.com",
					flow: "recovery",
				}),
			}),
		);
		expect(result.message).toBe("Recovery code sent");
	});

	it("verifies a registration code through the backend api", async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response(JSON.stringify({ message: "Verified" }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			}),
		);

		const result = await confirmRegistrationVerificationCode(
			"user@test.com",
			"123456",
		);

		expect(fetch).toHaveBeenCalledWith(
			"http://localhost:8080/api/v1/auth/verify-verification-code",
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({
					email: "user@test.com",
					code: "123456",
					flow: "registration",
				}),
			}),
		);
		expect(result.message).toBe("Verified");
	});

	it("returns a reset token after recovery code verification", async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response(
				JSON.stringify({
					message: "Recovery code accepted",
					resetToken: "token-123",
				}),
				{
					status: 200,
					headers: { "Content-Type": "application/json" },
				},
			),
		);

		const result = await confirmPasswordRecoveryCode("user@test.com", "123456");

		expect(result).toEqual({
			message: "Recovery code accepted",
			resetToken: "token-123",
		});
	});

	it("fails recovery verification when backend does not provide a reset token", async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response(JSON.stringify({ message: "ok" }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			}),
		);

		await expect(
			confirmPasswordRecoveryCode("user@test.com", "123456"),
		).rejects.toThrow("Backend did not return a password reset token");
	});

	it("sends a reset password request through the backend api", async () => {
		vi.mocked(fetch).mockResolvedValue(
			new Response(JSON.stringify({ message: "Password updated" }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			}),
		);

		const result = await completePasswordRecoveryReset(
			"user@test.com",
			"12345678",
			"12345678",
			"reset-token",
		);

		expect(fetch).toHaveBeenCalledWith(
			"http://localhost:8080/api/v1/auth/reset-password",
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({
					email: "user@test.com",
					password: "12345678",
					resetToken: "reset-token",
				}),
			}),
		);
		expect(result.message).toBe("Password updated");
	});
});
