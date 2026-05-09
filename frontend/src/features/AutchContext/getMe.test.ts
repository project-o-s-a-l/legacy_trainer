import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/shared/api/config", () => ({
	API_V1_BASE_URL: "http://localhost:8080/api/v1",
}));

import { getMe } from "./getMe";

describe("getMe", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		vi.clearAllMocks();
	});

	it("returns user when response is ok", async () => {
		const mockUser = {
			email: "test@example.com",
			username: "testuser",
			lastSeen: "2023-05-02T12:00:00Z",
			memberSince: "2023-04-01T12:00:00Z",
			isOnline: true,
			point: 50,
		};

		vi.mocked(globalThis.fetch).mockResolvedValue({
			ok: true,
			status: 200,
			json: vi.fn().mockResolvedValue(mockUser),
		} as unknown as Response);

		const result = await getMe();

		expect(globalThis.fetch).toHaveBeenCalledTimes(1);

		expect(globalThis.fetch).toHaveBeenCalledWith(
			"http://localhost:8080/api/v1/users/me",
			{
				method: "GET",
				credentials: "include",
				headers: {
					Accept: "application/json",
				},
				signal: undefined,
			},
		);

		expect(result).toEqual(mockUser);
	});

	it("returns null when response status is 401", async () => {
		vi.mocked(globalThis.fetch).mockResolvedValue({
			ok: false,
			status: 401,
			json: vi.fn(),
		} as unknown as Response);

		const result = await getMe();

		expect(result).toBeNull();
	});

	it("throws error when response is not ok and status is not 401", async () => {
		vi.mocked(globalThis.fetch).mockResolvedValue({
			ok: false,
			status: 500,
			json: vi.fn(),
		} as unknown as Response);

		await expect(getMe()).rejects.toThrow(
			"Failed to fetch current user",
		);
	});
});