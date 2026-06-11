import { describe, it, expect, vi, afterEach } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { fetchProfileInfo } from "./getProfileInfo";

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: {
			"Content-Type": "application/json",
		},
	});
}

describe("fetchProfileInfo", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("must call fetch with correct url and options", async () => {
		const profileResponse = {
			id: 1,
			username: "whitefox",
			email: "whitefox@example.com",
		};
		const progressResponse = {
			tasksCompleted: {
				easy: 2,
				medium: 1,
				hard: 0,
			},
			averageGrade: {
				easy: 90,
				medium: 80,
				hard: 0,
			},
		};

		const fetchMock = vi
			.spyOn(globalThis, "fetch")
			.mockResolvedValueOnce(jsonResponse(profileResponse))
			.mockResolvedValueOnce(jsonResponse(progressResponse));

		const controller = new AbortController();

		await fetchProfileInfo(controller.signal);

		expect(fetchMock).toHaveBeenNthCalledWith(
			1,
			"http://localhost:8080/api/v1/users/me",
			{
				method: "GET",
				credentials: "include",
				signal: controller.signal,
			},
		);
		expect(fetchMock).toHaveBeenNthCalledWith(
			2,
			"http://localhost:8080/api/v1/users/me/progress",
			{
				method: "GET",
				credentials: "include",
				signal: controller.signal,
			},
		);
	});

	it("must throw error if status is 401", async () => {
		vi.spyOn(globalThis, "fetch")
			.mockResolvedValueOnce(new Response(null, { status: 401 }))
			.mockResolvedValueOnce(new Response(null, { status: 200 }));

		await expect(fetchProfileInfo()).rejects.toThrow("Unauthorized");
	});

	it("must throw Failed to fetch profile info if status is 500", async () => {
		vi.spyOn(globalThis, "fetch")
			.mockResolvedValueOnce(new Response(null, { status: 500 }))
			.mockResolvedValueOnce(jsonResponse({}));

		await expect(fetchProfileInfo()).rejects.toThrow(
			"Failed to fetch profile info",
		);
	});

	it("must throw network error", async () => {
		vi.spyOn(globalThis, "fetch").mockRejectedValue(
			new Error("Network Error"),
		);

		await expect(fetchProfileInfo()).rejects.toThrow("Network Error");
	});
});
