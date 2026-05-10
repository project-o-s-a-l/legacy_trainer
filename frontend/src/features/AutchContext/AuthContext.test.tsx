import { fireEvent, screen, waitFor, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider, useAuth } from "./AuthContext";
import { getMe } from "./getMe";

vi.mock("./getMe.ts", () => ({
	getMe: vi.fn(),
}));

const mockedGetMe = vi.mocked(getMe);

function TestConsumer() {
	const { user, isAuthenticated, loading, refreshAuth, logout } = useAuth();

	return (
		<div>
			<div data-testid="loading">{String(loading)}</div>
			<div data-testid="is-authenticated">{String(isAuthenticated)}</div>
			<div data-testid="user-email">{user?.email ?? "null"}</div>

			<button type="button" onClick={() => void refreshAuth()}>
				refresh
			</button>

			<button type="button" onClick={() => void logout()}>
				logout
			</button>
		</div>
	);
}

describe("AuthProvider", () => {
	const orignalFetch = globalThis.fetch;

	beforeEach(() => {
		globalThis.fetch = vi.fn();
		vi.clearAllMocks();
	});

	afterEach(() => {
		globalThis.fetch = orignalFetch;
	});

	it("calls getMe on mount and sets authenticated user", async () => {
		mockedGetMe.mockResolvedValue({
			id: 1,
			email: "test@exapmle.com",
			username: "testuser",
			lastSeen: "2023-04-01T12:00:00Z",
			memberSince: "2023-03-01T12:00:00Z",
			isOnline: false,
			points: 0,
		} as any);

		render(
			<AuthProvider>
				<TestConsumer />
			</AuthProvider>,
		);

		expect(screen.getByTestId("loading")).toHaveTextContent("true");

		await waitFor(() => {
			expect(mockedGetMe).toHaveBeenCalledTimes(1);
		});

		await waitFor(() => {
			expect(screen.getByTestId("loading")).toHaveTextContent("false");
		});

		expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
			"true",
		);
		expect(screen.getByTestId("user-email")).toHaveTextContent(
			"test@exapmle.com",
		);
	});

	it("sets unauthenticated state whe getMe returns null", async () => {
		mockedGetMe.mockResolvedValue(null);

		render(
			<AuthProvider>
				<TestConsumer />
			</AuthProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("loading")).toHaveTextContent("false");
		});

		expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
			"false",
		);
		expect(screen.getByTestId("user-email")).toHaveTextContent("null");
	});

	it("handles getMe, error and finishes loading", async () => {
		mockedGetMe.mockResolvedValueOnce(null).mockResolvedValueOnce({
			email: "newuser@example.com",
			username: "newuser",
			lastSeen: "2023-10-05T12:00Z",
			memberSince: "2023-05-05T12:00Z",
			isOnline: false,
			points: 0,
		} as any);

		render(
			<AuthProvider>
				<TestConsumer />
			</AuthProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("loading")).toHaveTextContent("false");
		});

		expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
			"false",
		);
		expect(screen.getByTestId("user-email")).toHaveTextContent("null");

		fireEvent.click(screen.getByRole("button", { name: "refresh" }));

		await waitFor(() => {
			expect(mockedGetMe).toHaveBeenCalledTimes(2);
		});

		await waitFor(() => {
			expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
				"true",
			);
		});

		expect(screen.getByTestId("user-email")).toHaveTextContent(
			"newuser@example.com",
		);
	});

	it("logout send request and clear user", async () => {
		mockedGetMe.mockResolvedValue({
			email: "newuser@example.com",
			username: "new_user",
			lastSeen: "2023-10-05T12:00Z",
			memberSince: "2023-05-05T12:00Z",
			isOnline: true,
			points: 1000,
		} as any);

		vi.mocked(globalThis.fetch).mockResolvedValue({
			ok: true,
		} as Response);

		render(
			<AuthProvider>
				<TestConsumer />
			</AuthProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
				"true",
			);
		});

		fireEvent.click(screen.getByRole("button", { name: "logout" }));

		await waitFor(() => {
			expect(globalThis.fetch).toHaveBeenCalledTimes(1);
		});

		expect(globalThis.fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/auth/logout"),
			{
				method: "POST",
				credentials: "include",
			},
		);

		await waitFor(() => {
			expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
				"false",
			);
		});

		expect(screen.getByTestId("user-email")).toHaveTextContent("null");
	});

	it("clears user event if logout request fails", async () => {
		const consoleErrorSpy = vi
			.spyOn(console, "error")
			.mockImplementation(() => {});

		mockedGetMe.mockResolvedValue({
			email: "newuser@example.com",
			username: "new_user",
			lastSeen: "2023-10-05T12:00Z",
			memberSince: "2023-05-05T12:00Z",
			isOnline: true,
			points: 1000,
		} as any);

		vi.mocked(globalThis.fetch).mockRejectedValue(
			new Error("Logout failed"),
		);

		render(
			<AuthProvider>
				<TestConsumer />
			</AuthProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
				"true",
			);
		});

		fireEvent.click(screen.getByRole("button", { name: "logout" }));

		await waitFor(() => {
			expect(screen.getByTestId("is-authenticated")).toHaveTextContent(
				"false",
			);
		});

		expect(screen.getByTestId("user-email")).toHaveTextContent("null");
		expect(consoleErrorSpy).toHaveBeenCalled();

		consoleErrorSpy.mockRestore();
	});
});

describe("useAuth", () => {
	it("throws error when used outside AuthProvider", () => {
		const consoleErrorSpy = vi
			.spyOn(console, "error")
			.mockImplementation(() => {});

		function TestComponent() {
			useAuth();
			return null;
		}

		expect(() => render(<TestComponent />)).toThrow(
			"useAuth must be used inside AuthProvider",
		);

		consoleErrorSpy.mockRestore();
	});
});