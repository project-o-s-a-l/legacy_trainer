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
		expect(
			screen.getByRole("button", { name: "Toggle task filters" }),
		).toBeInTheDocument();
	});

	it("toggles choose list visibility by clicking the whole filter block", () => {
		render(<ChooseTask />);

		const toggleBlock = screen.getByRole("button", {
			name: "Toggle task filters",
		});
		fireEvent.click(toggleBlock);

		expect(toggleBlock).toHaveAttribute("aria-expanded", "true");
		expect(screen.getByText("v")).toBeInTheDocument();
	});

	it("toggles choose list visibility by keyboard on the filter block", () => {
		render(<ChooseTask />);

		const toggleBlock = screen.getByRole("button", {
			name: "Toggle task filters",
		});
		fireEvent.keyDown(toggleBlock, { key: "Enter" });

		expect(toggleBlock).toHaveAttribute("aria-expanded", "true");
	});

	it("updates chose language", () => {
		render(<ChooseTask />);

		fireEvent.click(
			screen.getByRole("button", { name: "Toggle task filters" }),
		);
		fireEvent.click(screen.getByRole("button", { name: "Python" }));

		expect(screen.getByText("Chose: Python")).toBeInTheDocument();
	});

	it("updates chosen difficulty", () => {
		render(<ChooseTask />);

		fireEvent.click(
			screen.getByRole("button", { name: "Toggle task filters" }),
		);
		fireEvent.click(screen.getByRole("button", { name: "Hard" }));

		expect(screen.getByText("Chose: Hard")).toBeInTheDocument();
	});

	it("updates chosen language and difficulty together", () => {
		render(<ChooseTask />);

		fireEvent.click(
			screen.getByRole("button", { name: "Toggle task filters" }),
		);
		fireEvent.click(screen.getByRole("button", { name: "Python" }));
		fireEvent.click(screen.getByRole("button", { name: "Hard" }));

		expect(screen.getByText("Chose: Python Hard")).toBeInTheDocument();
	});

	it("marks selected options as pressed", () => {
		render(<ChooseTask />);

		fireEvent.click(
			screen.getByRole("button", { name: "Toggle task filters" }),
		);

		const pythonOption = screen.getByRole("button", { name: "Python" });
		const hardOption = screen.getByRole("button", { name: "Hard" });

		fireEvent.click(pythonOption);
		fireEvent.click(hardOption);

		expect(pythonOption).toHaveAttribute("aria-pressed", "true");
		expect(pythonOption).toHaveClass("choose-task-option--selected");
		expect(hardOption).toHaveAttribute("aria-pressed", "true");
		expect(hardOption).toHaveClass("choose-task-option--selected");
	});

	it("navigates to CodeBlock with selected state", async () => {
		render(<ChooseTask />);

		fireEvent.click(
			screen.getByRole("button", { name: "Toggle task filters" }),
		);
		fireEvent.click(screen.getByRole("button", { name: "Python" }));
		fireEvent.click(screen.getByRole("button", { name: "Medium" }));
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

		fireEvent.click(
			screen.getByRole("button", { name: "Toggle task filters" }),
		);
		fireEvent.click(screen.getByRole("button", { name: "C++" }));
		fireEvent.click(screen.getByRole("button", { name: "Easy" }));

		expect(screen.getByText("Chose: C++ Easy")).toBeInTheDocument();

		fireEvent.click(screen.getByRole("button", { name: "Clear choose" }));

		expect(screen.getByText("Chose:")).toBeInTheDocument();
	});
});
