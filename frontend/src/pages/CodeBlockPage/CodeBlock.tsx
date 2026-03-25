import Editor, { useMonaco } from "@monaco-editor/react";
import React, { useState, useRef, useEffect } from "react";
import type { CodeBlockProps } from "./model/types.ts";
import { BLUE_LIGHT_THEME_NAME, blueLightTheme } from "./lib/blueLightTheme.ts";

export const CodeBlock: React.FC<CodeBlockProps> = ({
	language = "javascript",
	defaultValue = "",
	onChange,
	height = "800px",
	theme = "light",
}) => {
	const [code, setCode] = useState(defaultValue);

	const handelEditorChange = (value: string | undefined) => {
		const newValue = value || "";
		setCode(newValue);
		onChange?.(newValue);
	};

	const monaco = useMonaco();

	useEffect(() => {
		if (!monaco) return;

		monaco.editor.defineTheme(BLUE_LIGHT_THEME_NAME, blueLightTheme);
		monaco.editor.setTheme(BLUE_LIGHT_THEME_NAME);
	}, [monaco]);

	return (
		<div
			style={{
				display: "flex",
				gap: "16px",
				margin: "0, 10px, 0, 16px",
			}}
		>
			<div
				style={{
					width: "100%",
					height: "100%",
					overflowY: "auto",
					border: "1px solid #cccccc",
					boxSizing: "border-box",
					backgroundColor: "#96CCFF8A",
					// padding: 12,
					scrollbarWidth: "thin",
					scrollbarColor: "#5aa9e6 #96ccff8a",
				}}
			>
				<div
					style={{
						height: "800px",
						width: "850px",
						boxSizing: "border-box",
						// minHeight: "800px",
						// flexShrink: 0,
					}}
				>
					{/* TODO: Get task */}
					<span>
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! velit nobis odit possimus!
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! velit nobis odit possimus!
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! velit nobis odit possimus!
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! velit nobis odit possimus!
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! velit nobis odit possimus!
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! velit nobis odit possimus!
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! velit nobis odit possimus!
						Lorem ipsum dolor sit amet, consectetur adipisicing
						elit. Vel quae minus eligendi et quidem dolorum sapiente
						quod voluptates molestiae enim maiores ipsum
						praesentium, similique quos accusantium velit nobis odit
						possimus! Lorem ipsum dolor sit amet, consectetur
						adipisicing elit. Vel quae minus eligendi et quidem
						dolorum sapiente quod voluptates molestiae enim maiores
						ipsum praesentium, similique quos accusantium velit
						nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus! Lorem ipsum dolor sit amet,
						consectetur adipisicing elit. Vel quae minus eligendi et
						quidem dolorum sapiente quod voluptates molestiae enim
						maiores ipsum praesentium, similique quos accusantium
						velit nobis odit possimus!
					</span>
				</div>
			</div>
			<Editor
				key={language}
				language={language}
				value={code}
				height={height}
				theme={theme}
				onChange={handelEditorChange}
				// options={{
				// 	minimap: { enabled: false },
				// 	fontSize: 14,
				// 	lineNumbers: "on",
				// 	scrollBeyondLastLine: false,
				// 	automaticLayout: true,
				// 	tabSize: 2,
				// 	wordWrap: "on",
				// }}
				// loading={<div style={{ padding: "20px" }}>Загрузка...</div>}
			/>
		</div>
	);
};
