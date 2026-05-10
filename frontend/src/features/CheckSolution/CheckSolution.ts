import { API_V1_BASE_URL } from "@/shared/api/config";

export type CheckSolutionProps = {
	ok: boolean;
	message: string;
	testPassed: number;
};

export async function checkSolution(
	code: string,
	language: string,
	taskLevel: string,
): Promise<CheckSolutionProps> {
	const response = await fetch(`${API_V1_BASE_URL}/submission/check`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		credentials: "include",
		body: JSON.stringify({
			code,
			language,
			taskLevel,
		}),
	});

	let data: CheckSolutionProps | null = null;

	try {
		data = await response.json();
	} catch {
		data = null;
	}

	if (!response.ok) {
		throw new Error(
			data?.message || "Server error while checking solution",
		);
	}

	if (!data) {
		throw new Error("Server can`t return solution score");
	}

	return data;
}