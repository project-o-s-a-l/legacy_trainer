import { describe, expect, it } from "vitest";
import { getErrorMessage } from "./getErrorMessage";

describe("getErrorMessage", () => {
	it("returns the message field when present", async () => {
		const response = new Response(
			JSON.stringify({ message: "Top-level message" }),
			{
				headers: {
					"Content-Type": "application/json",
				},
			},
		);

		await expect(getErrorMessage(response, "Fallback")).resolves.toBe(
			"Top-level message",
		);
	});

	it("returns the detail string when present", async () => {
		const response = new Response(JSON.stringify({ detail: "Detail message" }), {
			headers: {
				"Content-Type": "application/json",
			},
		});

		await expect(getErrorMessage(response, "Fallback")).resolves.toBe(
			"Detail message",
		);
	});

	it("joins validation messages from a detail array", async () => {
		const response = new Response(
			JSON.stringify({
				detail: [{ msg: "Email is invalid" }, { msg: "Password is short" }],
			}),
			{
				headers: {
					"Content-Type": "application/json",
				},
			},
		);

		await expect(getErrorMessage(response, "Fallback")).resolves.toBe(
			"Email is invalid, Password is short",
		);
	});

	it("falls back to plain text when JSON parsing fails", async () => {
		const response = new Response("Plain text error");

		await expect(getErrorMessage(response, "Fallback")).resolves.toBe(
			"Plain text error",
		);
	});

	it("returns the fallback message when the response body is empty", async () => {
		const response = new Response("");

		await expect(getErrorMessage(response, "Fallback")).resolves.toBe(
			"Fallback",
		);
	});
});
