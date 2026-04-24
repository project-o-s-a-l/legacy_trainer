import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/AuthContext";
import ProtectedRoute from "../ProtectedRoute/ProtectedRoute";
import { Children } from "react";

vi.mock("@/features/AutchContext/AuthContext", () => ({
	useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

describe("ProtectedRoute", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("Show loading, if auth checking", () => {
		mockedUseAuth.mockReturnValue({
			isAuthenticated: false,
			loading: true,
			user: null,
			login: vi.fn(),
			logout: vi.fn(),
		} as any);

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
		mockedUseAuth.mockReturnValue({
			isAuthenticated: false,
			loading: false,
			user: null,
			login: vi.fn(),
			logout: vi.fn(),
		} as any);

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
		mockedUseAuth.mockReturnValue({
			isAuthenticated: true,
			loading: false,
			user: {
				email: "test@test.com",
				username: "testuser",
				lastSeen: "2023-10-001T12:34:56Z",
				memberSince: "2023-09-001T12:30Z",
				isOnline: true,
				points: 100,
			},
			login: vi.fn(),
			logout: vi.fn(),
		} as any);

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
