import type {
	ChangeEvent,
	HTMLAttributes,
	PropsWithChildren,
} from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { CodeBlock } from "./CodeBlock";
import { BLUE_LIGHT_THEME_NAME, blueLightTheme } from "./lib/blueLightTheme";

type EditorMockProps = {
	language?: string;
	height?: string | number;
	theme?: string;
	value?: string;
	onChange?: (value: string | undefined) => void;
};

type MockGroupProps = PropsWithChildren<HTMLAttributes<HTMLDivElement>>;
type MockPanelProps = PropsWithChildren;
type MockSeparatorProps = HTMLAttributes<HTMLDivElement>;

const monacoSpies = vi.hoisted(() => ({
	defineTheme: vi.fn(),
	setTheme: vi.fn(),
}));

vi.mock("@monaco-editor/react", () => ({
	__esModule: true,
	default: (props: EditorMockProps) => (
		<textarea
			data-testid="editor"
			data-language={props.language}
			data-height={props.height}
			data-theme={props.theme}
			value={props.value}
			onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
				props.onChange?.(e.target.value)
			}
		/>
	),
	useMonaco: () => ({
		editor: {
			defineTheme: monacoSpies.defineTheme,
			setTheme: monacoSpies.setTheme,
		},
	}),
}));

vi.mock("react-resizable-panels", () => ({
	Group: ({ children, ...props }: MockGroupProps) => (
		<div data-testid="group" {...props}>
			{children}
		</div>
	),
	Panel: ({ children }: MockPanelProps) => <div>{children}</div>,
	Separator: (props: MockSeparatorProps) => (
		<div data-testid="separator" {...props} />
	),
}));

describe("CodeBlock", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		Object.defineProperty(window, "innerWidth", {
			configurable: true,
			writable: true,
			value: 1400,
		});
	});

	it("renders task title and Solution header", () => {
		render(
			<CodeBlock
				task={{
					title: "Two Sum",
					description: "Find two numbers that add up to target.",
				}}
			/>,
		);

		expect(screen.getByText("Two Sum")).toBeInTheDocument();
		expect(screen.getByText("Solution:")).toBeInTheDocument();
	});

	it("renders initial editor value from defaultValue", () => {
		render(<CodeBlock defaultValue={"const a = 1;"} />);

		expect(screen.getByTestId("editor")).toHaveValue("const a = 1;");
	});

	it("calls onChange when user edits the code", () => {
		const onChange = vi.fn();
		render(<CodeBlock defaultValue="old code" onChange={onChange} />);

		fireEvent.change(screen.getByTestId("editor"), {
			target: { value: "new code" },
		});
		expect(onChange).toHaveBeenCalledTimes(1);
		expect(onChange).toHaveBeenCalledWith("new code");
		expect(screen.getByTestId("editor")).toHaveValue("new code");
	});

	it("passes language, height and theme props to editor", () => {
		render(
			<CodeBlock
				language="typescript"
				height="500px"
				theme="light"
				defaultValue="let x: number = 1"
			/>,
		);

		const editor = screen.getByTestId("editor");

		expect(editor).toHaveAttribute("data-language", "typescript");
		expect(editor).toHaveAttribute("data-height", "500px");
		expect(editor).toHaveAttribute("data-theme", BLUE_LIGHT_THEME_NAME);
	});

	it("registers and applies custom monaco theme on mount", () => {
		render(<CodeBlock />);

		expect(monacoSpies.defineTheme).toHaveBeenCalledWith(
			BLUE_LIGHT_THEME_NAME,
			blueLightTheme,
		);
		expect(monacoSpies.setTheme).toHaveBeenCalledWith(
			BLUE_LIGHT_THEME_NAME,
		);
	});

	it("renders resize layout shell", () => {
		render(<CodeBlock />);

		expect(screen.getByTestId("group")).toBeInTheDocument();
		expect(screen.getByTestId("separator")).toBeInTheDocument();
	});
});
