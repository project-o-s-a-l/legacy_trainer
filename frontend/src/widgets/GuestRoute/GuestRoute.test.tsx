import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/AuthContext";
import GuestRoute from "../GuestRoute/GuestRoute";

vi.mock("@/features/AutchContext/AuthContext", () => ({
	useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

describe("GuestRoute", () => {
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
							<GuestRoute>
								<div>Guest page</div>
							</GuestRoute>
						}
					/>
				</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByText("loading....")).toBeInTheDocument();
		expect(screen.queryByText("Guest page")).not.toBeInTheDocument();
	});

	it("render children< if user not auth", () => {
		mockedUseAuth.mockReturnValue({
			isAuthenticated: false,
			loading: false,
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
							<GuestRoute>
								<div>Guest page</div>
							</GuestRoute>
						}
					/>
				</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByText("Guest page")).toBeInTheDocument();
	});

	it("redirect on /profile, if user auth", () => {
		mockedUseAuth.mockReturnValue({
			isAuthenticated: true,
			loading: false,
			user: {
				email: "test@test.com",
				username: "testuser",
				lastSeen: "2023-10-05T12:34:00Z",
				memberSince: "2023-09-01T00:00:00",
				isOnline: true,
				points: 0,
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
							<GuestRoute>
								<div>Guest page</div>
							</GuestRoute>
						}
					/>
					<Route path="/profile" element={<div>Profile page</div>} />
				</Routes>
			</MemoryRouter>,
		);

		expect(screen.getByText("Profile page")).toBeInTheDocument();
		expect(screen.queryByText("Guest page")).not.toBeInTheDocument();
	});
});
