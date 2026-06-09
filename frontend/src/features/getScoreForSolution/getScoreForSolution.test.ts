import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { getScore, type SolutionResultsProps } from "./getScoreForSolution.ts";

const SUBMISSION_ID = 73;

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: {
			"Content-Type": "application/json",
		},
	});
}

describe("getScore", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("response GET for submission and checks", async () => {
		const submission = {
			id: SUBMISSION_ID,
			taskId: 11,
			userId: 7,
			language: "python",
			status: "passed",
			score: 90,
			submittedAt: "2026-06-09T12:00:00.000Z",
			checkedAt: "2026-06-09T12:00:05.000Z",
			memoryUsedKb: 128,
			executionTimeMs: 42,
		};
		const checks = [
			{
				id: 1,
				checkType: "tests",
				status: "passed",
				score: 90,
				report: {
					total: 10,
					passed: 9,
					failed: 1,
				},
				createdAt: "2026-06-09T12:00:05.000Z",
			},
		];

		const fetchMock = vi.mocked(fetch);
		fetchMock
			.mockResolvedValueOnce(jsonResponse(submission))
			.mockResolvedValueOnce(jsonResponse(checks));

		await getScore(SUBMISSION_ID);

		expect(fetchMock).toHaveBeenCalledTimes(2);
		expect(fetchMock).toHaveBeenNthCalledWith(
			1,
			`http://localhost:8080/api/v1/submissions/${SUBMISSION_ID}`,
			{
				method: "GET",
				credentials: "include",
			},
		);
		expect(fetchMock).toHaveBeenNthCalledWith(
			2,
			`http://localhost:8080/api/v1/submissions/${SUBMISSION_ID}/checks`,
			{
				method: "GET",
				credentials: "include",
			},
		);
	});

	it("return score, if server response is ok", async () => {
		const submission = {
			id: SUBMISSION_ID,
			taskId: 11,
			userId: 7,
			language: "typescript",
			status: "passed",
			score: 88,
			submittedAt: "2026-06-09T12:00:00.000Z",
			checkedAt: "2026-06-09T12:00:05.000Z",
			memoryUsedKb: 256,
			executionTimeMs: 55,
		};
		const checks = [
			{
				id: 1,
				checkType: "tests",
				status: "passed",
				score: 88,
				report: {
					total: 12,
					passed: 11,
					failed: 1,
					details: [{ name: "test_valid_input", status: "passed" }],
				},
				createdAt: "2026-06-09T12:00:05.000Z",
			},
		];
		const responseData: SolutionResultsProps = {
			submission,
			checks,
			totalTests: 12,
			testsPassed: 11,
			failedTests: 1,
			overallScore: 88,
		};

		vi.mocked(fetch)
			.mockResolvedValueOnce(jsonResponse(submission))
			.mockResolvedValueOnce(jsonResponse(checks));

		const result = await getScore(SUBMISSION_ID);

		expect(result).toEqual(responseData);
	});

	it("Throws error, if submission response is not ok", async () => {
		vi.mocked(fetch)
			.mockResolvedValueOnce(new Response("", { status: 500 }))
			.mockResolvedValueOnce(jsonResponse([]));

		await expect(getScore(SUBMISSION_ID)).rejects.toThrow(
			"Failed to fetch submission result",
		);
	});

	it("Throws error, if fetch down stream", async () => {
		vi.mocked(fetch).mockRejectedValue(new Error("Network error"));

		await expect(getScore(SUBMISSION_ID)).rejects.toThrow("Network error");
	});
});
