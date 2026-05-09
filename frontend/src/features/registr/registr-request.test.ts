import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { register_request } from "./registr-request";

describe("register_request", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("must return data on a successful response", async () => {
		const fakeResponse = {
			message: "User registered successfully",
			token: "test-token",
		};

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			status: 200,
			statusText: "OK",
			text: vi.fn().mockResolvedValue(JSON.stringify(fakeResponse)),
		} as unknown as Response);

		const result = await register_request(
			"admin",
			"admin@test.com",
			"1234",
		);

		expect(fetch).toHaveBeenCalledWith(
			"http://localhost:8080/api/v1/auth/register",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Accept: "application/json",
				},
				body: JSON.stringify({
					username: "admin",
					email: "admin@test.com",
					password: "1234",
				}),
			},
		);

		expect(result).toEqual(fakeResponse);
	});

	it("must throw an error on a failed response", async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 400,
			statusText: "Bad Request",
			text: vi.fn().mockResolvedValue("User already exists"),
		} as unknown as Response);

		await expect(
			register_request("admin", "admin@test.com", "wrong"),
		).rejects.toThrow(
			"Registration failed: 400 Bad Request User already exists",
		);
	});
});