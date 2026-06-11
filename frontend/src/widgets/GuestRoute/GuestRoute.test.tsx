import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/useAuth";
import type { User } from "@/features/AutchContext/getMe.types";
import GuestRoute from "../GuestRoute/GuestRoute";

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

describe("GuestRoute", () => {
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
		mockedUseAuth.mockReturnValue(createAuthState());

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
		mockedUseAuth.mockReturnValue(
			createAuthState(
				{
					isAuthenticated: true,
				},
				{
					email: "test@test.com",
					username: "testuser",
					lastSeen: "2023-10-05T12:34:00Z",
					memberSince: "2023-09-01T00:00:00",
					isOnline: true,
					points: 0,
				},
			),
		);

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
