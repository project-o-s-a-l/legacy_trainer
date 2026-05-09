import type { Profile } from "@/pages/ProfilePage/lib/profileInterface";
import { API_V1_BASE_URL } from "@/shared/api/config";

export async function fetchProfileInfo(signal?: AbortSignal): Promise<Profile> {
	const response = await fetch(`${API_V1_BASE_URL}/users/me`, {
		method: "GET",
		credentials: "include",
		signal,
	});
	if (response.status === 401) {
		throw new Error("Unauthorized");
	}

	if (!response.ok) {
		throw new Error("Failed to fetch profile info");
	}

	const profileInfo = await response.json();
	return {
		...profileInfo,
		tasksCompleted: profileInfo.tasksCompleted ?? {
			easy: 0,
			medium: 0,
			hard: 0,
		},
		averageGrade: profileInfo.averageGrade ?? {
			easy: 0,
			medium: 0,
			hard: 0
		},
	};
}
