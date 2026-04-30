import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { checkSolution, type CheckSolutionProps } from "./CheckSolution";

const API_URL = "http://localhost:8080/api/runSolutionTests";

function mockResponse(body: unknown, ok = true): Response {
	return {
		ok,
		json: vi.fn().mockResolvedValue(body),
	} as unknown as Response;
}

function mockInvalidJsonResponse(ok = true): Response {
	return {
		ok,
		json: vi.fn().mockRejectedValue(new SyntaxError("Invalid JSON")),
	} as unknown as Response;
}

describe("checkSolution", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("response POST with code, language and taskLevel", async () => {
		const responseData: CheckSolutionProps = {
			ok: true,
			message: "All tests passed",
			testPassed: 5,
		};

		const fetchMock = vi.mocked(fetch);
		fetchMock.mockResolvedValueOnce(mockResponse(responseData));

		await checkSolution("print('hello')", "python", "easy");

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
				taskLevel: "easy"
			}),
		});
	});

	it("return data, if server response is ok", async () => {
	const responseData: CheckSolutionProps = {
			ok: true,
			message: "Success",
			testPassed: 3,
		};

		vi.mocked(fetch).mockResolvedValueOnce(mockResponse(responseData));

		const result = await checkSolution("def test(): pass", "python", "medium");

		expect(result).toEqual(responseData);
	});

	it("throw error with message server, if response not ok", async () => {
		const responseData: CheckSolutionProps = {
			ok: false,
			message: "Compilation error",
			testPassed: 0
		};

		vi.mocked(fetch).mockResolvedValueOnce(mockResponse(responseData, false));

		await expect(
			checkSolution("test_fun(): return 5", "python", "easy")
		).rejects.toThrow("Compilation error");
	});

	it("Throws default error if response not ok and JSON not parsing", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(mockInvalidJsonResponse(false));

		await expect(
			checkSolution("broken code", "python", "easy")
		).rejects.toThrow("Server error while checking solution");
	});

	it("Throws error if response is ok< but server not request a JSON", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(mockInvalidJsonResponse(true));

		await expect(
			checkSolution("print('hello')", "python", "easy")
		).rejects.toThrow("Server can`t return solution score");
	});
});
