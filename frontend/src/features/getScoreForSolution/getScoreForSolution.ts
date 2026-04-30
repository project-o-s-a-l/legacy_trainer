const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://localhost:8080";


export type SolutionResultsProps = {
	Architecture: number;
	CodeLogic: number;
	Standards: number;
};


export async function getScore(): Promise<SolutionResultsProps>{
	const response = await fetch(`${API_BASE_URL}/api/getScore`, {
		method: "GET",
		credentials: "include",
	});

	if(!response.ok) {
		throw new Error("Failed to fetch score");
	}

	return response.json();
}