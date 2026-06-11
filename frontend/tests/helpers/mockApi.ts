import type { Page, Request } from "@playwright/test";

type MockUser = {
	id: number;
	username: string;
	email: string;
	memberSince: string;
	lastSeen: string;
	isOnline: boolean;
	points: number;
	avatarUrl?: string | null;
};

type RequestLogEntry = {
	method: string;
	pathname: string;
	search: string;
	body: unknown;
};

type MockApiOptions = {
	initialUser?: MockUser | null;
};

const defaultUser: MockUser = {
	id: 7,
	username: "testuser",
	email: "testuser@example.com",
	memberSince: "2025-01-10T10:00:00.000Z",
	lastSeen: "2026-06-11T09:00:00.000Z",
	isOnline: true,
	points: 1500,
	avatarUrl: null,
};

const taskResponse = {
	id: 101,
	title: "Refactor legacy loop",
	description: "Replace the loop with a cleaner implementation.",
	requirements: "Keep the same output and preserve performance.",
	legacyCode: "def solve(items):\n    return len(items)\n",
	language: "python",
	difficulty: "Medium",
};

const submissionResult = {
	submissionId: 555,
	taskId: 101,
	status: "passed",
	score: 90,
	message: "All visible tests passed",
	testPassed: 5,
};

const submissionDetails = {
	id: 555,
	taskId: 101,
	userId: 7,
	language: "python",
	status: "passed",
	score: 90,
	submittedAt: "2026-06-11T10:00:00.000Z",
	checkedAt: "2026-06-11T10:00:01.000Z",
	memoryUsedKb: 128,
	executionTimeMs: 32,
};

const submissionChecks = [
	{
		id: 1,
		checkType: "tests",
		status: "passed",
		score: 90,
		report: {
			total: 5,
			passed: 5,
			failed: 0,
			details: [
				{ name: "test_handles_empty_list", status: "passed" },
				{ name: "test_counts_items", status: "passed" },
			],
		},
		createdAt: "2026-06-11T10:00:01.000Z",
	},
];

function jsonResponse(body: unknown, status = 200) {
	return {
		status,
		contentType: "application/json",
		body: JSON.stringify(body),
	};
}

async function readJsonBody(request: Request) {
	const body = request.postData();
	return body ? JSON.parse(body) : null;
}

export async function setupMockApi(
	page: Page,
	options: MockApiOptions = {},
) {
	let currentUser = options.initialUser ?? null;
	const requestLog: RequestLogEntry[] = [];

	await page.route("**/api/v1/**", async (route) => {
		const request = route.request();
		const url = new URL(request.url());
		const { pathname, search } = url;
		const method = request.method();

		const body =
			method === "POST" || method === "PUT" || method === "PATCH"
				? await readJsonBody(request)
				: null;

		requestLog.push({
			method,
			pathname,
			search,
			body,
		});

		if (pathname === "/api/v1/users/me" && method === "GET") {
			if (!currentUser) {
				await route.fulfill(jsonResponse({ detail: "Unauthorized" }, 401));
				return;
			}

			await route.fulfill(jsonResponse(currentUser));
			return;
		}

		if (pathname === "/api/v1/users/me/progress" && method === "GET") {
			await route.fulfill(
				jsonResponse({
					tasksCompleted: {
						easy: 4,
						medium: 3,
						hard: 1,
					},
					averageGrade: {
						easy: 95,
						medium: 88,
						hard: 84,
					},
				}),
			);
			return;
		}

		if (pathname === "/api/v1/auth/login" && method === "POST") {
			currentUser = { ...defaultUser };
			await route.fulfill(jsonResponse({ token: "session-token" }));
			return;
		}

		if (pathname === "/api/v1/auth/logout" && method === "POST") {
			currentUser = null;
			await route.fulfill(jsonResponse({ message: "Logged out" }));
			return;
		}

		if (pathname === "/api/v1/auth/register" && method === "POST") {
			const requestBody = body as {
				username: string;
				email: string;
			};

			await route.fulfill(
				jsonResponse({
					message: "User registered successfully",
					user: {
						id: 17,
						username: requestBody.username,
						email: requestBody.email,
					},
				}),
			);
			return;
		}

		if (
			pathname === "/api/v1/auth/request-verification-code" &&
			method === "POST"
		) {
			await route.fulfill(
				jsonResponse({
					message: "Verification code sent",
				}),
			);
			return;
		}

		if (
			pathname === "/api/v1/auth/verify-verification-code" &&
			method === "POST"
		) {
			const requestBody = body as { flow: "registration" | "recovery" };

			if (requestBody.flow === "recovery") {
				await route.fulfill(
					jsonResponse({
						message: "Recovery code verified",
						resetToken: "reset-token-123",
					}),
				);
				return;
			}

			await route.fulfill(
				jsonResponse({
					message: "Registration completed",
				}),
			);
			return;
		}

		if (pathname === "/api/v1/auth/reset-password" && method === "POST") {
			await route.fulfill(
				jsonResponse({
					message: "Password updated",
				}),
			);
			return;
		}

		if (pathname === "/api/v1/tasks" && method === "GET") {
			await route.fulfill(jsonResponse(taskResponse));
			return;
		}

		if (pathname === "/api/v1/tasks/101/submit" && method === "POST") {
			await route.fulfill(jsonResponse(submissionResult));
			return;
		}

		if (pathname === "/api/v1/submissions/555/checks" && method === "GET") {
			await route.fulfill(jsonResponse(submissionChecks));
			return;
		}

		if (pathname === "/api/v1/submissions/555" && method === "GET") {
			await route.fulfill(jsonResponse(submissionDetails));
			return;
		}

		await route.fulfill(jsonResponse({ detail: "Unhandled mock route" }, 500));
	});

	return {
		requestLog,
		getCurrentUser: () => currentUser,
	};
}
