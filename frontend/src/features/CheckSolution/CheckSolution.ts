const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

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
	const response = await fetch(`${API_BASE_URL}/api/runSolutionTests`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		credentials: "include",
		body: JSON.stringify({
			code: code,
			language: language,
			taskLevel: taskLevel,
		}),
	});

	const data: CheckSolutionProps = await response.json();

	if (!response.ok) {
		throw new Error("Failed to check solution");
	}

	return data;
}
