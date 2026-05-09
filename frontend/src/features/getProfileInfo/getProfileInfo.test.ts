import { describe, it, expect, vi, afterEach } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { fetchProfileInfo } from "./getProfileInfo";

describe("fetchProfileInfo", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("must call fetch with correct url and options", async () => {
		const mockResponse = {
			id: 1,
			username: "whitefox",
			email: "whitefox@example.com",
		};

		const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
			new Response(JSON.stringify(mockResponse), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			}),
		);

		const controller = new AbortController();

		await fetchProfileInfo(controller.signal);

		expect(fetchMock).toHaveBeenCalledWith(
			"http://localhost:8080/api/v1/users/me",
			{
				method: "GET",
				credentials: "include",
				signal: controller.signal,
			},
		);
	});

	it("must throw error if status is 401", async () => {
		vi.spyOn(globalThis, "fetch").mockResolvedValue(
			new Response(null, { status: 401 }),
		);

		await expect(fetchProfileInfo()).rejects.toThrow("Unauthorized");
	});

	it("must throw Failed to fetch profile info if status is 500", async () => {
		vi.spyOn(globalThis, "fetch").mockResolvedValue(
			new Response(null, { status: 500 }),
		);

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