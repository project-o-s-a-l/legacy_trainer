import { API_V1_BASE_URL } from "@/shared/api/config";
import { getErrorMessage } from "@/shared/api/getErrorMessage";

export type VerificationFlowMode = "registration" | "recovery";

type VerificationRequestResponse = {
	message: string;
};

type VerificationConfirmResponse = {
	message: string;
	resetToken?: string;
};

type ResetPasswordResponse = {
	message: string;
};

async function postJson<TResponse>(
	url: string,
	payload: Record<string, string>,
	fallbackMessage: string,
) {
	let response: Response;

	try {
		response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Accept: "application/json",
			},
			body: JSON.stringify(payload),
		});
	} catch {
		throw new Error("Unable to reach the backend");
	}

	if (!response.ok) {
		throw new Error(await getErrorMessage(response, fallbackMessage));
	}

	return response.json() as Promise<TResponse>;
}

function validateEmail(email: string) {
	if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
		throw new Error("Enter a valid email address");
	}
}

function validateCode(code: string) {
	if (!/^\d{4,6}$/.test(code.trim())) {
		throw new Error("Enter a valid verification code");
	}
}

export async function requestRegistrationVerificationCode(email: string) {
	validateEmail(email);

	return postJson<VerificationRequestResponse>(
		`${API_V1_BASE_URL}/auth/request-verification-code`,
		{
			email: email.trim().toLowerCase(),
			flow: "registration",
		},
		"Unable to request registration verification code",
	);
}

export async function requestPasswordRecoveryCode(email: string) {
	validateEmail(email);

	return postJson<VerificationRequestResponse>(
		`${API_V1_BASE_URL}/auth/request-verification-code`,
		{
			email: email.trim().toLowerCase(),
			flow: "recovery",
		},
		"Unable to request password recovery code",
	);
}

export async function confirmRegistrationVerificationCode(
	email: string,
	code: string,
) {
	validateEmail(email);
	validateCode(code);

	return postJson<VerificationConfirmResponse>(
		`${API_V1_BASE_URL}/auth/verify-verification-code`,
		{
			email: email.trim().toLowerCase(),
			code: code.trim(),
			flow: "registration",
		},
		"Unable to verify registration code",
	);
}

export async function confirmPasswordRecoveryCode(email: string, code: string) {
	validateEmail(email);
	validateCode(code);

	const response = await postJson<VerificationConfirmResponse>(
		`${API_V1_BASE_URL}/auth/verify-verification-code`,
		{
			email: email.trim().toLowerCase(),
			code: code.trim(),
			flow: "recovery",
		},
		"Unable to verify password recovery code",
	);

	if (!response.resetToken?.trim()) {
		throw new Error("Backend did not return a password reset token");
	}

	return {
		message: response.message,
		resetToken: response.resetToken,
	};
}

export async function completePasswordRecoveryReset(
	email: string,
	password: string,
	confirmPassword: string,
	resetToken: string,
) {
	validateEmail(email);

	if (password.trim().length < 8) {
		throw new Error("Password must be at least 8 characters long");
	}

	if (password !== confirmPassword) {
		throw new Error("Passwords do not match");
	}

	if (!resetToken.trim()) {
		throw new Error("Missing password reset token");
	}

	return postJson<ResetPasswordResponse>(
		`${API_V1_BASE_URL}/auth/reset-password`,
		{
			email: email.trim().toLowerCase(),
			password,
			resetToken: resetToken.trim(),
		},
		"Unable to reset password",
	);
}
