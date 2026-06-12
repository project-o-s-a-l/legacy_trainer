import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import Profile from "./Profile";
import { fetchProfileInfo } from "@/features/getProfileInfo/getProfileInfo";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
	const actual =
		await vi.importActual<typeof import("react-router-dom")>(
			"react-router-dom",
		);

	return {
		...actual,
		useNavigate: () => mockNavigate,
	};
});

vi.mock("@/features/getProfileInfo/getProfileInfo", () => ({
	fetchProfileInfo: vi.fn(),
}));

const mockedFetchProfileInfo = vi.mocked(fetchProfileInfo);

const profileMock = {
	username: "whitefox",
	email: "whitefox@exapmle.com",
	memberSince: "2024-01-10",
	lastSeen: "2026-04-20",
	isOnline: true,
	avatarUrl: "/avatar.png",
	points: 1500,
	tasksCompleted: {
		easy: 10,
		medium: 5,
		hard: 2,
	},
	averageGrade: {
		easy: 95,
		medium: 88,
		hard: 80,
	},
};

function formatDate(value: string | null) {
	if (!value) {
		return "n/a";
	}

	return new Intl.DateTimeFormat("en-GB", {
		dateStyle: "medium",
		timeStyle: "short",
	}).format(new Date(value));
}

function renderProfile() {
	return render(
		<MemoryRouter>
			<Profile />
		</MemoryRouter>,
	);
}

describe("Profile", () => {
	beforeEach(() => {
		vi.clearAllMocks();

		vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:test-preview");
		vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {});
		vi.spyOn(window, "alert").mockImplementation(() => {});
	});

	afterEach(() => {
		vi.resetAllMocks();
	});

	it("render loading state", () => {
		mockedFetchProfileInfo.mockReturnValue(new Promise(() => {}));

		renderProfile();

		expect(screen.getByText("Loading...")).toBeInTheDocument();
	});

	it("render success profile", async () => {
		mockedFetchProfileInfo.mockResolvedValue(profileMock);

		renderProfile();

		const formattedMemberSince = formatDate(profileMock.memberSince);
		const formattedLastSeen = formatDate(profileMock.lastSeen);

		expect(
			await screen.findByText(profileMock.username),
		).toBeInTheDocument();
		expect(screen.getAllByText(profileMock.email)).toHaveLength(2);
		expect(screen.getByText(`Member since ${formattedMemberSince}`)).toBeInTheDocument();
		expect(screen.getByText(`Last seen ${formattedLastSeen}`)).toBeInTheDocument();
		expect(screen.getAllByText(formattedMemberSince)).toHaveLength(1);
		expect(screen.getAllByText(formattedLastSeen)).toHaveLength(1);
		expect(screen.getByText("online")).toBeInTheDocument();
		expect(screen.getByText("Online now")).toBeInTheDocument();
		expect(screen.getByText("Points")).toBeInTheDocument();
		expect(screen.getByText(profileMock.points.toString())).toBeInTheDocument();
		expect(
			screen.queryByRole("button", { name: "Settings" }),
		).not.toBeInTheDocument();

		const img = screen.getByAltText("Profile Image") as HTMLImageElement;
		expect(img.src).toContain(profileMock.avatarUrl);
	});

	it("redirect on /login if unauthorized", async () => {
		mockedFetchProfileInfo.mockRejectedValue(new Error("Unauthorized"));

		renderProfile();
		await waitFor(() => {
			expect(mockNavigate).toHaveBeenCalledWith("/login", {
				replace: true,
			});
		});
	});

	it("Show fallback error message if fetch fails", async () => {
		mockedFetchProfileInfo.mockRejectedValue(new Error("Server exploded"));

		renderProfile();

		expect(
			await screen.findByText("Failed to load profile information"),
		).toBeInTheDocument();
	});

	it("Change avatar preview on file select", async () => {
		mockedFetchProfileInfo.mockResolvedValue(profileMock);

		renderProfile();
		await screen.findByText("whitefox");

		const input = screen.getByTestId("avatar-input") as HTMLInputElement;
		const file = new File(["avatar"], "avatar.png", { type: "image/png" });

		fireEvent.change(input, {
			target: {
				files: [file],
			},
		});

		const avatar = screen.getByAltText("Profile Image");
		expect(URL.createObjectURL).toHaveBeenCalledWith(file);
		expect(avatar).toHaveAttribute("src", "blob:test-preview");
	});

	it("Show alert on invalid file type", async () => {
		mockedFetchProfileInfo.mockResolvedValue(profileMock);

		renderProfile();
		await screen.findByText("whitefox");

		const input = screen.getByTestId("avatar-input") as HTMLInputElement;
		const badFile = new File(["text"], "notes.txt", { type: "text/plain" });

		fireEvent.change(input, {
			target: {
				files: [badFile],
			},
		});

		expect(window.alert).toHaveBeenCalledWith(
			"Пожалуйста, выберите файл в формате PNG или JPG",
		);
	});

	it("Free blod URL on unmount", async () => {
		mockedFetchProfileInfo.mockResolvedValue(profileMock);

		const { unmount } = renderProfile();
		await screen.findByText("whitefox");
		const input = screen.getByTestId("avatar-input") as HTMLInputElement;
		const file = new File(["avatar"], "avatar.png", { type: "image/png" });

		fireEvent.change(input, {
			target: {
				files: [file],
			},
		});

		unmount();

		expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:test-preview");
	});
});
