import type { RegisterResponse } from "@/shared";
import { API_V1_BASE_URL } from "@/shared/api/config";

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

	const responseText = await response.text();

	if (!response.ok) {
		console.error("REGISTER FAILED:", {
			status: response.status,
			statusText: response.statusText,
			body: responseText,
		});

		throw new Error(
			`Registration failed: ${response.status} ${response.statusText} ${responseText}`,
		);
	}
  	return JSON.parse(responseText) as RegisterResponse;
}
