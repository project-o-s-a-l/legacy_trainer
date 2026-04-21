import type { Profile } from "@/pages/ProfilePage/lib/profileInterface";

export async function fetchProfileInfo(signal?: AbortSignal): Promise<Profile> {
	const response = await fetch("/api/profile/info", {
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
	return profileInfo;
}
