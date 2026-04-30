const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

export type TaskResponse = {
	id: string;
	title: string;
	description: string;
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

	const response = await fetch(`${API_BASE_URL}/api/getTask?${params}`, {
		method: "GET",
		credentials: "include",
	});

	if (!response.ok) {
		throw new Error("Get task failed");
	}

	return response.json();
}
