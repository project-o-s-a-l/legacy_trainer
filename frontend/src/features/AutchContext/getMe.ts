// import type { User } from "./getMe.types";
// import { API_V1_BASE_URL } from "@/shared/api/config";

// export async function getMe(token: string): Promise<User | null> {
// 	const response = await fetch(`${API_V1_BASE_URL}/auth/me`, {
// 		method: "GET",
// 		credentials: "include",
// 		headers: {
// 			Accept: "application/json",
// 		},
// 		body: JSON.stringify({
// 			token,
// 		}),
// 	});

// 	if (response.status === 401) {
// 		return null;
// 	}

// 	if (!response.ok) {
// 		  throw new Error("Not authenticated");
// 	}

// 	return response.json();
// }

import type { User } from "./getMe.types";
import { API_V1_BASE_URL } from "@/shared/api/config";

export async function getMe(): Promise<User | null> {
	const response = await fetch(`${API_V1_BASE_URL}/users/me`, {
		method: "GET",
		credentials: "include",
		headers: {
			Accept: "application/json",
		},
	});

	if (response.status === 401) {
		return null;
	}

	if (!response.ok) {
		throw new Error("Failed to fetch current user");
	}

	return response.json();
}