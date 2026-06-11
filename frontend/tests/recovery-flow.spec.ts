import { expect, test } from "@playwright/test";
import { setupMockApi } from "./helpers/mockApi";

test("forgot password and reset flow returns the user to login", async ({
	page,
}) => {
	const { requestLog } = await setupMockApi(page);

	await page.goto("/forgot-password");

	await page.getByLabel("Email").fill("recover@example.com");
	await page.getByRole("button", { name: "Send code" }).click();

	await page.waitForURL("**/confirm-email");
	await expect(page.getByText("Password recovery")).toBeVisible();
	await expect(
		page.getByText("Code destination: recover@example.com"),
	).toBeVisible();

	await page.getByLabel("Verification code").fill("654321");
	await page.getByRole("button", { name: "Next" }).click();

	await page.waitForURL("**/reset-password");
	await expect(
		page.getByRole("heading", { name: "Reset password" }),
	).toBeVisible();

	await page
		.getByLabel("New password", { exact: true })
		.fill("newSecret123");
	await page
		.getByLabel("Confirm new password", { exact: true })
		.fill("newSecret123");
	await page.getByRole("button", { name: "Save password" }).click();

	await page.waitForURL("**/login");
	await expect(page.getByText("Password updated")).toBeVisible();

	const requestCodeCalls = requestLog.filter(
		(entry) =>
			entry.pathname === "/api/v1/auth/request-verification-code" &&
			entry.method === "POST",
	);
	const confirmRecoveryRequest = requestLog.find(
		(entry) =>
			entry.pathname === "/api/v1/auth/verify-verification-code" &&
			entry.method === "POST",
	);
	const resetRequest = requestLog.find(
		(entry) =>
			entry.pathname === "/api/v1/auth/reset-password" &&
			entry.method === "POST",
	);

	expect(requestCodeCalls.at(-1)?.body).toEqual({
		email: "recover@example.com",
		flow: "recovery",
	});
	expect(confirmRecoveryRequest?.body).toEqual({
		email: "recover@example.com",
		code: "654321",
		flow: "recovery",
	});
	expect(resetRequest?.body).toEqual({
		email: "recover@example.com",
		password: "newSecret123",
		resetToken: "reset-token-123",
	});
});
