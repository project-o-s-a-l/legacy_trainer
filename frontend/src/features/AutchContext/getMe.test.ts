import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getMe } from "./getMe";

describe("getMe", () => {
	const orignalFetch = globalThis.fetch;

	beforeEach(() => {
		globalThis.fetch = vi.fn();
	});

	afterEach(() => {
		globalThis.fetch = orignalFetch;
		vi.clearAllMocks();
	});

	it("returns user when response is ok", async () => {
		const mockUser = {
			email: "test@emxample.com",
			username: "testuser",
			lastSeen: "2023-05-02T12:00:00Z",
			memberSince: "2023-04-01T12:00:00Z",
			isOnline: true,
			point: 50
		};


		vi.mocked(globalThis.fetch).mockResolvedValue({
			ok:true,
			status: 200,
			json: vi.fn().mockResolvedValue(mockUser),
		} as unknown as Response);

		const result = await getMe();

		expect(globalThis.fetch).toHaveBeenCalledTimes(1);
		expect(globalThis.fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/auth/me"),
			{
				method: "GET",
				credentials: "include",
				signal: undefined,
			},
		);

		expect(result).toEqual(mockUser);
	});

	it("throws error when response is not ok and status is not 401", async () => {
		vi.mocked(globalThis.fetch).mockResolvedValue({
			ok: false,
			status: 500,
			json: vi.fn(),
		} as unknown as Response);

		await expect(getMe()).rejects.toThrow("Failed to fetch user");
	});

	it("passes abort signal to fetch", async () => {
		const controller = new AbortController();

		vi.mocked(globalThis.fetch).mockResolvedValue({
			ok: false,
			status: 401,
			json: vi.fn(),
		} as unknown as Response);

		await getMe(controller.signal);

		expect(globalThis.fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/auth/me"), {
				method: "GET",
				credentials: "include",
				signal: controller.signal
			},
		);
	});
});