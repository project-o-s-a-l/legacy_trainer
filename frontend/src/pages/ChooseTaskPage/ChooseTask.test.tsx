import type { MouseEventHandler, ReactNode } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import ChooseTask from "./ChooseTask";

const { navigateMock, getTaskMock } = vi.hoisted(() => ({
	navigateMock: vi.fn(),
	getTaskMock: vi.fn(),
}));

vi.mock("react-router-dom", () => ({
	useNavigate: () => navigateMock,
}));

vi.mock("@/features/getTask/getTask", () => ({
	getTask: getTaskMock,
}));

type MockButtonProps = {
	children: ReactNode;
	onClick?: MouseEventHandler<HTMLButtonElement>;
	className?: string;
};

vi.mock("@/shared", () => ({
	Button: ({ children, onClick, className }: MockButtonProps) => (
		<button onClick={onClick} className={className}>
			{children}
		</button>
	),
}));

vi.mock(
	"@/shared/assets/images/svg/matrix-static-dense-gray-transparent.svg",
	() => ({
		default: "matrix.svg",
	}),
);

describe("ChooseTask", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.stubGlobal("alert", vi.fn());

		getTaskMock.mockResolvedValue({
			title: "Test task",
			description: "Solve test task",
		});
	});

	it("renders main UI elements", () => {
		render(<ChooseTask />);

		expect(
			screen.getByText("Choose a programming language"),
		).toBeInTheDocument();
		expect(screen.getByText("Difficulty level")).toBeInTheDocument();
		expect(
			screen.getByText("Get a task and start working"),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: "Generate a task" }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: "Clear choose" }),
		).toBeInTheDocument();
		expect(screen.getByRole("button", { name: ">" })).toBeInTheDocument();
	});

	it("toggles choose list visibility", () => {
		render(<ChooseTask />);

		const toggleButton = screen.getByRole("button", { name: ">" });
		fireEvent.click(toggleButton);

		expect(screen.getByRole("button", { name: "v" })).toBeInTheDocument();
	});

	it("updates chose language", () => {
		render(<ChooseTask />);

		fireEvent.click(screen.getByText("Python"));

		expect(screen.getByText("Chose: Python")).toBeInTheDocument();
	});

	it("updates chosen difficulty", () => {
		render(<ChooseTask />);

		fireEvent.click(screen.getByText("Hard"));

		expect(screen.getByText("Chose: Hard")).toBeInTheDocument();
	});

	it("updates chosen language and difficulty together", () => {
		render(<ChooseTask />);

		fireEvent.click(screen.getByText("Python"));
		fireEvent.click(screen.getByText("Hard"));

		expect(screen.getByText("Chose: Python Hard")).toBeInTheDocument();
	});

	it("navigates to CodeBlock with selected state", async () => {
		render(<ChooseTask />);

		fireEvent.click(screen.getByText("Python"));
		fireEvent.click(screen.getByText("Medium"));
		fireEvent.click(
			screen.getByRole("button", { name: "Generate a task" }),
		);

		await waitFor(() => {
			expect(getTaskMock).toHaveBeenCalledWith("Python", "Medium");
		});

		await waitFor(() => {
			expect(navigateMock).toHaveBeenCalledWith("/CodeBlock", {
				state: {
					chooseLanguage: "Python",
					chooseDificulty: "Medium",
					task: {
						title: "Test task",
						description: "Solve test task",
					},
				},
			});
		});
	});

	it("shows alert and does not navigate when selection is incomplete", () => {
		render(<ChooseTask />);

		fireEvent.click(
			screen.getByRole("button", { name: "Generate a task" }),
		);

		expect(alert).toHaveBeenCalledWith(
			"Please choose language and difficulty",
		);
		expect(navigateMock).not.toHaveBeenCalled();
		expect(getTaskMock).not.toHaveBeenCalled();
	});

	it("clears chosen values", () => {
		render(<ChooseTask />);

		fireEvent.click(screen.getByText("C++"));
		fireEvent.click(screen.getByText("Easy"));

		expect(screen.getByText("Chose: C++ Easy")).toBeInTheDocument();

		fireEvent.click(screen.getByRole("button", { name: "Clear choose" }));

		expect(screen.getByText("Chose:")).toBeInTheDocument();
	});
});
