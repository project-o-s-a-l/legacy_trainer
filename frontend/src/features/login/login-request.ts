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
		throw new Error("Login Failed"); //TODO: Изменить
	}

	const data: LoginResponse = await response.json();

	localStorage.setItem("token", data.token);

	return data;
}

// Все это не в этом файле
// TODO: getProfile. Нужен JWT-token для получения информации о пользователе.
// TODO: getMyProblems. Нужен JWT-token;
// TODO: getMySettings. Нужен JWT-token;
// TODO: CreateProblem. Нужен JWT-token;
// TODO: reloadProfile. Нужен JWT-token;
// TODO: admin. Нужен JWT-token, с доп. проверками "role == admin";
// TODO: getMySolutions. Нужен JWT-token;
// TODO: getMyStatistic. Нужен JWT-token;
// TODO: getMyScoreByAI. Нужен JWT-token;
// TODO: Доразобратся в erd-диаграмме