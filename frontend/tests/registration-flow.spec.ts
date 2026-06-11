import { expect, test } from "@playwright/test";
import { setupMockApi } from "./helpers/mockApi";

test("registration and email verification flow reaches login notice", async ({
	page,
}) => {
	const { requestLog } = await setupMockApi(page);

	await page.goto("/Registration");

	await page.getByPlaceholder("Enter username").fill("newuser");
	await page.getByPlaceholder("Enter email").fill("newuser@example.com");
	await page.getByPlaceholder("Enter password").fill("secret123");
	await page.getByPlaceholder("Confirm your password").fill("secret123");
	await page.getByRole("button", { name: "Get code" }).click();

	await page.waitForURL("**/confirm-email");
	await expect(page.getByText("Confirm your email")).toBeVisible();
	await expect(
		page.getByText("Code destination: newuser@example.com"),
	).toBeVisible();

	await page.getByLabel("Verification code").fill("123456");
	await page.getByRole("button", { name: "Next" }).click();

	await page.waitForURL("**/login");
	await expect(
		page.getByText("Registration completed"),
	).toBeVisible();

	const registerRequest = requestLog.find(
		(entry) =>
			entry.pathname === "/api/v1/auth/register" && entry.method === "POST",
	);
	const verifyCodeRequest = requestLog.find(
		(entry) =>
			entry.pathname === "/api/v1/auth/request-verification-code" &&
			entry.method === "POST",
	);
	const confirmRequest = requestLog.find(
		(entry) =>
			entry.pathname === "/api/v1/auth/verify-verification-code" &&
			entry.method === "POST",
	);

	expect(registerRequest?.body).toEqual({
		username: "newuser",
		email: "newuser@example.com",
		password: "secret123",
	});
	expect(verifyCodeRequest?.body).toEqual({
		email: "newuser@example.com",
		flow: "registration",
	});
	expect(confirmRequest?.body).toEqual({
		email: "newuser@example.com",
		code: "123456",
		flow: "registration",
	});
});
