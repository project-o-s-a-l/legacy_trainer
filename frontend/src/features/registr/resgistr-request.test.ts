import { describe, it, expect, vi, beforeEach } from "vitest";
import { register_request } from "./registr-request.ts";

describe("register_request", () => {
	beforeEach(() => {
		vi.resetAllMocks();
	});

	it("must return data on a successful response", async () => {
		const fakeResponse = {
			message: "User registered successfully",
			token: "test-token",
		};

		globalThis.fetch = vi.fn().mockResolvedValue({
			ok: true,
			json: vi.fn().mockResolvedValue(fakeResponse)
		} as unknown as Response);

		const result = await register_request(
			"admin",
			"admin@test.com",
			"1234"
		);

		expect(fetch).toHaveBeenCalledWith(
			"https://localhost:7032/api/register",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Accept: "application/json",
				},
				body: JSON.stringify({
					username: "admin",
					email: "admin@test.com",
					password: "1234"
				}),
			},
		);
		expect(result).toEqual(fakeResponse);
	});

	it("must throw an error on a failed response", async () => {
		globalThis.fetch = vi.fn().mockResolvedValue({
			ok: false,
		} as Response);

		await expect(
			register_request("admin", "admin@test.com", "wrong")
		).rejects.toThrow("Registration Failed");
	});
});