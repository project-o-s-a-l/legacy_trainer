import type { User } from "./getMe.types";
import { API_V1_BASE_URL } from "@/shared/api/config";

export async function getMe(signal?: AbortSignal) : Promise<User | null> {
	const response = await fetch(`${API_V1_BASE_URL}/auth/me`, {
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

