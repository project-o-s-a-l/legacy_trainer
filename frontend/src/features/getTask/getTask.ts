import { API_V1_BASE_URL } from "@/shared/api/config";

export type TaskResponse = {
	id: number;
	title: string;
	description: string;
	requirements: string;
	legacyCode: string | null;
	language: string;
	difficulty: string;
};


export async function getTask(
	language: string,
	difficulty: string,
): Promise<TaskResponse> {
	const params = new URLSearchParams({
		language,
		difficulty,
	});

	const response = await fetch(`${API_V1_BASE_URL}/tasks?${params}`, {
		method: "GET",
		credentials: "include",
	});

	if (!response.ok) {
		throw new Error("Get task failed");
	}

	return response.json();
}

