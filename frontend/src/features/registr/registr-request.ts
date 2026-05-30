import type { RegisterResponse } from "@/shared";
import { API_V1_BASE_URL } from "@/shared/api/config";
import { getErrorMessage } from "@/shared/api/getErrorMessage";

export async function register_request(
	username: string,
	email: string,
	password: string,
): Promise<RegisterResponse> {
	const response = await fetch(`${API_V1_BASE_URL}/auth/register`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		body: JSON.stringify({
			username: username,
			email: email,
			password: password,
		}),
	});

	if (!response.ok) {
		throw new Error(
			await getErrorMessage(response, "Registration failed"),
		);
	}

	return response.json() as Promise<RegisterResponse>;
}
