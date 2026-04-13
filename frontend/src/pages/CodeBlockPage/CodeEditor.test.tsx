import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import CodeEditor from "./CodeEditor";

const toggleNavbarMock = vi.fn();
const codeBlockMock = vi.fn();
const mockUseLocation = vi.fn();

vi.mock("react-router-dom", () => ({
	useLocation: () => mockUseLocation(),
}));

vi.mock("@/shared/lib/layout/NavbarContext", () => ({
	useNavbar: () => ({
		isNavbarVisible: true,
		toggleNavbar: toggleNavbarMock,
	}),
}));

vi.mock("./CodeBlock", () => ({
	CodeBlock: (props: any) => {
		codeBlockMock(props);
		return <div data-testid="code-block-mock">Mo</div>;
	},
}));

describe("CodeEditor", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mockUseLocation.mockReturnValue({ state: undefined });
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
			},
		});

		render(<CodeEditor />);

		expect(codeBlockMock).toHaveBeenCalledWith(
			expect.objectContaining({
				language: "python",
				defaultValue: "def hello_python():\n\tprint('Hello, World!')",
				height: "850px",
				theme: "blueLight",
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

		expect(
			screen.getByText("Language: Python|Difficulty: Easy"),
		).toBeInTheDocument();
	});
});
