import { expect, test } from "@playwright/test";
import { setupMockApi } from "./helpers/mockApi";

test("login and logout flow works through the real UI", async ({ page }) => {
	const { requestLog, getCurrentUser } = await setupMockApi(page);

	await page.goto("/login");

	await expect(
		page.getByRole("heading", { name: "Login" }),
	).toBeVisible();

	await page.getByLabel("Email or username").fill("testuser@example.com");
	await page.getByLabel("Password").fill("secret123");
	await page.getByRole("button", { name: "next" }).click();

	await page.waitForURL("**/");
	await expect(page.getByRole("button", { name: "Log out" })).toBeVisible();
	await expect(page.getByRole("link", { name: "Profile" })).toBeVisible();
	await expect(
		page.getByRole("link", { name: "ChooseTask" }),
	).toBeVisible();
	expect(getCurrentUser()?.email).toBe("testuser@example.com");

	const loginRequest = requestLog.find(
		(entry) =>
			entry.pathname === "/api/v1/auth/login" && entry.method === "POST",
	);

	expect(loginRequest?.body).toEqual({
		login: "testuser@example.com",
		password: "secret123",
	});

	await page.getByRole("button", { name: "Log out" }).click();

	await page.waitForURL("**/");
	await expect(page.getByRole("link", { name: "Registration" })).toBeVisible();
	await expect(page.getByRole("link", { name: "Login" })).toBeVisible();
	await expect(page.getByRole("button", { name: "Log out" })).toHaveCount(0);

	await page.goto("/profile");
	await page.waitForURL("**/login");
	await expect(
		page.getByRole("heading", { name: "Login" }),
	).toBeVisible();
});
