import type { Profile } from "@/pages/ProfilePage/lib/profileInterface";
import { API_V1_BASE_URL } from "@/shared/api/config";
import { getErrorMessage } from "@/shared/api/getErrorMessage";

export async function fetchProfileInfo(signal?: AbortSignal): Promise<Profile> {
	const [profileResponse, progressResponse] = await Promise.all([
		fetch(`${API_V1_BASE_URL}/users/me`, {
			method: "GET",
			credentials: "include",
			signal,
		}),
		fetch(`${API_V1_BASE_URL}/users/me/progress`, {
			method: "GET",
			credentials: "include",
			signal,
		}),
	]);

	if (
		profileResponse.status === 401 ||
		progressResponse.status === 401
	) {
		throw new Error("Unauthorized");
	}

	if (!profileResponse.ok) {
		throw new Error(
			await getErrorMessage(
				profileResponse,
				"Failed to fetch profile info",
			),
		);
	}

	const profileInfo = await profileResponse.json();
	const progressInfo = progressResponse.ok
		? await progressResponse.json()
		: null;

	return {
		...profileInfo,
		tasksCompleted: progressInfo?.tasksCompleted ?? {
			easy: 0,
			medium: 0,
			hard: 0,
		},
		averageGrade: progressInfo?.averageGrade ?? {
			easy: 0,
			medium: 0,
			hard: 0,
		},
	};
}
