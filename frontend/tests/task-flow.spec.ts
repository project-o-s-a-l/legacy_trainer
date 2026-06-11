import { expect, test } from "@playwright/test";
import { setupMockApi } from "./helpers/mockApi";

test("authenticated user can choose a task, submit it and open result page", async ({
	page,
}) => {
	const { requestLog } = await setupMockApi(page, {
		initialUser: {
			id: 7,
			username: "solver",
			email: "solver@example.com",
			memberSince: "2025-02-01T10:00:00.000Z",
			lastSeen: "2026-06-11T10:05:00.000Z",
			isOnline: true,
			points: 1700,
			avatarUrl: null,
		},
	});

	await page.goto("/ChooseTask");

	await expect(
		page.getByText("Choose a programming language"),
	).toBeVisible();
	await page.getByRole("button", { name: ">" }).click();
	await page.getByText("Python").click();
	await page.getByText("Medium").click();
	await page.getByRole("button", { name: "Generate a task" }).click();

	await page.waitForURL("**/CodeBlock");
	await expect(page.getByText("Refactor legacy loop")).toBeVisible();
	await expect(
		page.getByText("Language: Python|Difficulty: Medium"),
	).toBeVisible();

	await page.getByRole("button", { name: "Submit" }).click();

	await page.waitForURL("**/result");
	await expect(
		page.getByText("Refactor legacy loop scored 90 %"),
	).toBeVisible();
	await expect(
		page.getByText("You have been awarded 80 for this task"),
	).toBeVisible();
	await expect(
		page.getByText("All available backend checks passed."),
	).toBeVisible();
	await expect(page.getByText("test_handles_empty_list")).toBeVisible();
	await expect(page.getByLabel("Solution preview")).toContainText(
		"def solve(items):",
	);

	const getTaskRequest = requestLog.find(
		(entry) => entry.pathname === "/api/v1/tasks" && entry.method === "GET",
	);
	const submitRequest = requestLog.find(
		(entry) =>
			entry.pathname === "/api/v1/tasks/101/submit" &&
			entry.method === "POST",
	);

	expect(getTaskRequest?.search).toBe("?language=Python&difficulty=Medium");
	expect(submitRequest?.body).toEqual({
		code: "def solve(items):\n    return len(items)\n",
		language: "python",
	});
});
