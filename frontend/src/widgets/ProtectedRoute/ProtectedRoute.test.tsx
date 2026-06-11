import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/useAuth";
import type { User } from "@/features/AutchContext/getMe.types";
import ProtectedRoute from "../ProtectedRoute/ProtectedRoute";

vi.mock("@/features/AutchContext/useAuth", () => ({
	useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

type MockAuthState = ReturnType<typeof useAuth>;

function createAuthState(
	overrides: Partial<MockAuthState> = {},
	user: User | null = null,
): MockAuthState {
	return {
		isAuthenticated: false,
		loading: false,
		user,
		refreshAuth: async () => {},
		logout: async () => {},
		...overrides,
	};
}

describe("ProtectedRoute", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("Show loading, if auth checking", () => {
		mockedUseAuth.mockReturnValue(createAuthState({
			loading: true,
		}));

		render(
			<MemoryRouter initialEntries={["/login"]}>
				<Routes>
					<Route
						path="/login"
						element={
							<ProtectedRoute>
								<div>Protected page</div>
							</ProtectedRoute>
						}
					/>
				</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByText("Check auth....")).toBeInTheDocument();

		expect(screen.queryByText("Protected page")).not.toBeInTheDocument();
	});

	it("redirect on /login, if user not auth", () => {
		mockedUseAuth.mockReturnValue(createAuthState());

		render(
			<MemoryRouter initialEntries={["/profile"]}>
				<Routes>
					<Route
						path="/profile"
						element={
							<ProtectedRoute>
								<div>Protected page</div>
							</ProtectedRoute>
						}
					/>
					<Route path="/login" element={<div>Sign in page</div>} />
				</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByText("Sign in page")).toBeInTheDocument();
		expect(screen.queryByText("Protected page")).not.toBeInTheDocument();
	});

	it("render Children, if user auth", () => {
		mockedUseAuth.mockReturnValue(
			createAuthState(
				{
					isAuthenticated: true,
				},
				{
					email: "test@test.com",
					username: "testuser",
					lastSeen: "2023-10-001T12:34:56Z",
					memberSince: "2023-09-001T12:30Z",
					isOnline: true,
					points: 100,
				},
			),
		);

		render(
			<MemoryRouter initialEntries={["/login"]}>
				<Routes>
					<Route
						path="/login"
						element={
							<ProtectedRoute>
								<div>Protected page</div>
							</ProtectedRoute>
						}
					/>
				</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByText("Protected page")).toBeInTheDocument();
	});
});
