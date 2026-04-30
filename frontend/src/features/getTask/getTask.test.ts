import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { getTask, type TaskResponse } from "./getTask";


const API_URL = "http://localhost:8080/api/getTask";

function mockResponse(body: unknown, ok = true): Response {
	return {
		ok,
		json: vi.fn().mockResolvedValue(body),
	} as unknown as Response;
}

describe("getTask", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(()=> {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("response GET with language and difficulty in query params", async () => {
		const responseData: TaskResponse = {
			id: "1",
			title: "Two Sum",
			description: "Find two numbers that sum to target",
			language: "python",
			difficulty: "easy",
		};

		const fetchMock = vi.mocked(fetch);
		fetchMock.mockResolvedValueOnce(mockResponse(responseData));

		await getTask("python", "easy");

		expect(fetchMock).toHaveBeenCalledTimes(1);
		expect(fetchMock).toHaveBeenCalledWith(
			`${API_URL}?language=python&difficulty=easy`,
			{
				method: "GET",
				credentials: "include"
			},
		);
	});

	it("return the task, if server response is ok", async () => {
		const responseData: TaskResponse = {
			id: "task-123",
			title: "Reverse String",
			description: "Reverse the given string",
			language: "cpp",
			difficulty: "medium",
		};

		vi.mocked(fetch).mockResolvedValueOnce(mockResponse(responseData));

		const result = await getTask("cpp", "medium");

		expect(result).toEqual(responseData);
	});

	it("Throws error, if response not ok", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(mockResponse(null, false));

		await expect(getTask("python", "hard")).rejects.toThrow(
			"Get task failed"
		);
	});

	it("Throws error if fetch fails", async () => {
		vi.mocked(fetch).mockResolvedValueOnce(mockResponse(null, false));

		await expect(getTask("python", "hard")).rejects.toThrow(
			"Get task failed",
		);
	});

	it("correct parsing query params", async () => {
		const responseData: TaskResponse = {
			id: "2",
			title: "Task",
			description: "description",
			language: "C++",
			difficulty: "very hard",
		};

		const fetchMock = vi.mocked(fetch);
		fetchMock.mockResolvedValueOnce(mockResponse(responseData));

		await getTask("C++", "very hard");

		expect(fetchMock).toHaveBeenCalledWith(
			`${API_URL}?language=C%2B%2B&difficulty=very+hard`,
			{
				method: "GET",
				credentials: "include"
			}
		)
	});
});