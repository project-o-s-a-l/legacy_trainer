import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import CodeEditor from "./CodeEditor";
import type { CodeBlockProps } from "./model/types";

const { toggleNavbarMock, codeBlockMock, mockUseLocation, navigateMock } =
	vi.hoisted(() => ({
		toggleNavbarMock: vi.fn(),
		codeBlockMock: vi.fn(),
		mockUseLocation: vi.fn(),
		navigateMock: vi.fn(),
	}));

vi.mock("react-router-dom", () => ({
	useLocation: () => mockUseLocation(),
	useNavigate: () => navigateMock,
}));

vi.mock("@/shared/index", () => ({
	useNavbar: () => ({
		isNavbarVisible: true,
		toggleNavbar: toggleNavbarMock,
	}),
}));

vi.mock("./CodeBlock", () => ({
	CodeBlock: (props: CodeBlockProps) => {
		codeBlockMock(props);
		return <div data-testid="code-block-mock">Mock CodeBlock</div>;
	},
}));

describe("CodeEditor", () => {
	beforeEach(() => {
		vi.clearAllMocks();

		mockUseLocation.mockReturnValue({
			state: undefined,
		});
	});

	it("renders navbar toggle button with visible state", () => {
		render(<CodeEditor />);

		expect(screen.getByRole("button", { name: "^" })).toBeInTheDocument();
	});

	it("calls toggleNavbar when toggle button is clicked", () => {
		render(<CodeEditor />);

		fireEvent.click(screen.getByRole("button", { name: "^" }));

		expect(toggleNavbarMock).toHaveBeenCalledTimes(1);
	});

	it("passed correct props to CodeBlock", () => {
		render(<CodeEditor />);

		expect(screen.getByTestId("code-block-mock")).toBeInTheDocument();

		expect(codeBlockMock).toHaveBeenCalledWith(
			expect.objectContaining({
				language: "plaintext",
				defaultValue: "",
				height: "850px",
				theme: "blueLight",
				onChange: expect.any(Function),
			}),
		);
	});

	it("passed python props to CodeBlock when Python is selected", () => {
		mockUseLocation.mockReturnValue({
			state: {
				chooseLanguage: "Python",
				chooseDificulty: "Easy",
				task: {
					title: "Test task",
					description: "Test description",
					requirements: "Keep the public API unchanged",
					legacyCode: "def hello_python():\n\tprint('Hello, World!')",
				},
			},
		});

		render(<CodeEditor />);

		expect(codeBlockMock).toHaveBeenCalledWith(
			expect.objectContaining({
				language: "python",
				defaultValue: "def hello_python():\n\tprint('Hello, World!')",
				height: "850px",
				theme: "blueLight",
				task: expect.objectContaining({
					title: "Test task",
					description: "Test description",
					requirements: "Keep the public API unchanged",
				}),
				onChange: expect.any(Function),
			}),
		);
	});

	it("renders selected language and difficulty", () => {
		mockUseLocation.mockReturnValue({
			state: {
				chooseLanguage: "Python",
				chooseDificulty: "Easy",
			},
		});

		render(<CodeEditor />);

		expect(screen.getByText("Language: Python")).toBeInTheDocument();
		expect(screen.getByText("Difficulty: Easy")).toBeInTheDocument();
	});
});
