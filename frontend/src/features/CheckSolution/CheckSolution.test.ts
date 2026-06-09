import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { checkSolution, type CheckSolutionProps } from "./CheckSolution";

const TASK_ID = 42;
const API_URL = `http://localhost:8080/api/v1/tasks/${TASK_ID}/submit`;

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: {
			"Content-Type": "application/json",
		},
	});
}

describe("checkSolution", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("response POST with code and language", async () => {
		const responseData: CheckSolutionProps = {
			submissionId: 73,
			taskId: TASK_ID,
			status: "passed",
			score: 100,
			message: "All tests passed",
			testPassed: 5,
		};

		const fetchMock = vi.mocked(fetch);
		fetchMock.mockResolvedValueOnce(jsonResponse(responseData));

		await checkSolution(TASK_ID, "print('hello')", "python");

		expect(fetchMock).toHaveBeenCalledTimes(1);
		expect(fetchMock).toHaveBeenCalledWith(API_URL, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Accept: "application/json",
			},
			credentials: "include",
			body: JSON.stringify({
				code: "print('hello')",
				language: "python",
			}),
		});
	});

	it("return data, if server response is ok", async () => {
		const responseData: CheckSolutionProps = {
			submissionId: 15,
			taskId: TASK_ID,
			status: "queued",
			score: 60,
			message: "Success",
			testPassed: 3,
		};

		vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(responseData));

		const result = await checkSolution(TASK_ID, "def test(): pass", "python");

		expect(result).toEqual(responseData);
	});

	it("throw error with server message, if response not ok", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(
			jsonResponse({ message: "Compilation error" }, 400),
		);

		await expect(
			checkSolution(TASK_ID, "test_fun(): return 5", "python"),
		).rejects.toThrow("Compilation error");
	});

	it("Throws default error if response not ok and body is empty", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(new Response("", { status: 500 }));

		await expect(
			checkSolution(TASK_ID, "broken code", "python"),
		).rejects.toThrow("Server error while checking solution");
	});

	it("Throws error if response is ok, but server does not return JSON", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(new Response("", { status: 200 }));

		await expect(
			checkSolution(TASK_ID, "print('hello')", "python"),
		).rejects.toThrow("Server cannot return submission result");
	});
});
