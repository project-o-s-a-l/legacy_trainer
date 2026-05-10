import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { getScore, type SolutionResultsProps } from "./getScoreForSolution.ts";

const API_URL = "http://localhost:8080/api/v1/submissions/score";

function mockResponse(body: unknown, ok = true): Response {
	return {
		ok,
		json: vi.fn().mockResolvedValue(body),
	} as unknown as Response;
}

describe("getScore", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("response GET for get score", async () => {
		const responseData: SolutionResultsProps = {
			Architecture: 90,
			CodeLogic: 85,
			Standards: 80,
		};

		const fetchMock = vi.mocked(fetch);
		fetchMock.mockResolvedValueOnce(mockResponse(responseData));

		await getScore();

		expect(fetchMock).toHaveBeenCalledTimes(1);

		expect(fetchMock).toHaveBeenCalledWith(API_URL, {
			method: "GET",
			credentials: "include",
		});
	});

	it("return score, if server response is ok", async () => {
		const responseData: SolutionResultsProps = {
			Architecture: 75,
			CodeLogic: 95,
			Standards: 88,
		};

		vi.mocked(fetch).mockResolvedValueOnce(mockResponse(responseData));

		const result = await getScore();

		expect(result).toEqual(responseData);
	});

	it("Throws error, if response not ok", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(mockResponse(null, false));

		await expect(getScore()).rejects.toThrow("Failed to fetch score");
	});

	it("Throws error, if fetch down stream", async () => {
		vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));

		await expect(getScore()).rejects.toThrow("Network error");
	});
});