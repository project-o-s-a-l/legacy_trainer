import type { User } from "./getMe.types";

const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

export async function getMe(signal?: AbortSignal) : Promise<User | null> {
	const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
		method: "GET",
		credentials: "include",
		signal
	});

	if(response.status === 401) {
		return null;
	}

	if(!response.ok) {
		throw new Error("Failed to fetch user");
	}

	return response.json();
}

