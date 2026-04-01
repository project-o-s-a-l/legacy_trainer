import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import CodeEditor  from "./CodeEditor";

const toggleNavbarMock = vi.fn();
const codeBlockMock = vi.fn();

vi.mock("@/shared/lib/layout/NavbarContext", ()=> ({
	useNavbar: () => ({
		isNavbarVisible: true,
		toggleNavbar: toggleNavbarMock
	}),
}));

vi.mock("./CodeBlock", () => ({
	CodeBlock: (props: any) => {
		codeBlockMock(props);
		return <div data-testid="code-block-mock">Mo</div>
	},
}));

describe("CodeEditor", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders navbar toggle button with visible state", () => {
		render(<CodeEditor />)

		expect(screen.getByRole("button", { name: "^" })).toBeInTheDocument();
	});

	it("calls toggleNavbar when toggle button is clicked", () => {
		render(<CodeEditor />)

		fireEvent.click(screen.getByRole("button", { name: "^" }));

		expect(toggleNavbarMock).toHaveBeenCalledTimes(1);
	});

	it("passed correct props to CodeBlock", () => {
		render(<CodeEditor />);

		expect(screen.getByTestId("code-block-mock")).toBeInTheDocument();

		expect(codeBlockMock).toHaveBeenCalledWith(
			expect.objectContaining({
				language: "typescript",
				defaultValue: `console.log('Hello World!');`,
				height: "850px",
				theme: "blueLight",
				onChange: expect.any(Function),
			}),
		);
	});
});