import type { RegisterResponse } from "@/shared";

const API_BASE_URL = "https://localhost:7032/api"; // ЗАГЛУШКА

export async function register_request(
	username: string,
	email: string,
	password: string,
): Promise<RegisterResponse> {
	const response = await fetch(
		`${API_BASE_URL}/register`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Accept: "application/json",
			},
			body: JSON.stringify({
				username:username,
				email:email,
				password: password
			}),
		});
	if (!response.ok) {
		throw new Error("Registration Failed"); //TODO: Изменить
	}
	const data: RegisterResponse = await response.json();
	return data;
}
