import type { LoginResponse } from "@/shared";
import { API_V1_BASE_URL } from "@/shared/api/config";

export async function login_request(
	login: string,
	password: string,
): Promise<LoginResponse> {
	const response = await fetch(`${API_V1_BASE_URL}/auth/login`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		credentials: "include",
		body: JSON.stringify({
			login,
			password,
		}),
	});

	if (!response.ok) {
		throw new Error("Login failed");
	}

	return response.json();
}

// admin. Нужен JWT-token, с доп. проверками "role == admin";
// TODO: getMyScoreByAI. Нужен JWT-token;
// TODO: verifyEmailCode
