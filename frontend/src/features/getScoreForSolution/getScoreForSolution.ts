import { API_V1_BASE_URL } from "@/shared/api/config";


export type SolutionResultsProps = {
	Architecture: number;
	CodeLogic: number;
	Standards: number;
};


export async function getScore(): Promise<SolutionResultsProps>{
	const response = await fetch(`${API_V1_BASE_URL}/submissions/score`, {
		method: "GET",
		credentials: "include",
	});

	if(!response.ok) {
		throw new Error("Failed to fetch score");
	}

	return response.json();
}
