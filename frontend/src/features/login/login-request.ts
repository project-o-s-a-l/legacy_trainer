import type { LoginResponse } from "@/shared";

const API_BASE_URL = "https://localhost:7032/api"; // ЗАГЛУШКА

export async function login_request(login: string, password: string) {
	const response: Response = await fetch(`${API_BASE_URL}/login`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		credentials: "include",
		body: JSON.stringify({
			login: login,
			password: password,
		}),
	});

	if (!response.ok) {
		throw new Error("Login Failed");
	}

	const data: LoginResponse = await response.json();

	localStorage.setItem("token", data.token);

	return data;
}

// admin. Нужен JWT-token, с доп. проверками "role == admin"; 
// Все это не в этом файле
// TODO: getMyStatistic. Нужен JWT-token;
// TODO: getMyScoreByAI. Нужен JWT-token;
// TODO: verifyEmailCode
// TODO: getTask
// TODO: checkSolution