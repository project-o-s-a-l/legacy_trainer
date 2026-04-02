import { describe, it, expect, vi, beforeEach } from "vitest";
import { login_request } from "./login-request";

const localStorageMock = (() => {
	let store: Record<string, string> = {};

	return {
		getItem: vi.fn((key: string) => store[key] ?? null),
		setItem: vi.fn((key: string, value: string) => {
			store[key] = String(value);
		}),
		removeItem: vi.fn((key: string) => {
			delete store[key];
		}),
		clear: vi.fn(() => {
			store = {};
		}),
	};
})();

Object.defineProperty(globalThis, "localStorage", {
	value: localStorageMock,
	writable: true,
});

describe("login_request", () => {
	beforeEach(() => {
		vi.resetAllMocks();
		localStorage.clear();
	});

	it("must be save token on a successful response", async () => {
		const fakeResponse = {
			token: "test-token",
		};

		globalThis.fetch = vi.fn().mockResolvedValue({
			ok: true,
			json: vi.fn().mockResolvedValue(fakeResponse),
		} as unknown as Response);

		const result = await login_request("admin", "1234");

		expect(fetch).toHaveBeenCalledWith(
			"https://localhost:7032/api/login",
			expect.objectContaining({
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Accept: "application/json",
				},
			}),
		);

		expect(localStorage.getItem("token")).toBe("test-token");
		expect(result).toEqual(fakeResponse);
	});

	it("must throw an error on a failed response", async () => {
		globalThis.fetch = vi.fn().mockResolvedValue({
			ok: false,
		} as Response);

		await expect(login_request("admin", "wrong")).rejects.toThrow(
			"Login Failed",
		);
	});
});
