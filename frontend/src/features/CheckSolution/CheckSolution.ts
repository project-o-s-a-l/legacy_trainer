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