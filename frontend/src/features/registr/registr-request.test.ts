import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { register_request } from "./registr-request";

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: {
			"Content-Type": "application/json",
		},
	});
}

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
			user: {
				id: 1,
				username: "admin",
				email: "admin@test.com",
			},
		};

		vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(fakeResponse));

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
		vi.mocked(fetch).mockResolvedValueOnce(
			jsonResponse({ detail: "User already exists" }, 400),
		);

		await expect(
			register_request("admin", "admin@test.com", "wrong"),
		).rejects.toThrow("User already exists");
	});
});
