import { API_V1_BASE_URL } from "@/shared/api/config";
import { getErrorMessage } from "@/shared/api/getErrorMessage";

export type CheckSolutionProps = {
	submissionId: number;
	taskId: number;
	status: string;
	score: number;
	message: string;
	testPassed: number;
};

export async function checkSolution(
	taskId: number,
	code: string,
	language: string,
): Promise<CheckSolutionProps> {
	const response = await fetch(`${API_V1_BASE_URL}/tasks/${taskId}/submit`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
		},
		credentials: "include",
		body: JSON.stringify({
			code,
			language,
		}),
	});

	if (!response.ok) {
		throw new Error(
			await getErrorMessage(
				response,
				"Server error while checking solution",
			),
		);
	}

	let data: CheckSolutionProps | null = null;

	try {
		data = await response.json();
	} catch {
		data = null;
	}

	if (!data) {
		throw new Error("Server cannot return submission result");
	}

	return data;
}
