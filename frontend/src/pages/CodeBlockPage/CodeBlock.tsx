import Editor, { useMonaco } from "@monaco-editor/react";
import React, { useState, useRef, useEffect } from "react";
import type { CodeBlockProps } from "./model/types.ts";
import { BLUE_LIGHT_THEME_NAME, blueLightTheme } from "./lib/blueLightTheme.ts";
import { Group, Panel, Separator } from "react-resizable-panels";
import type { editor } from "monaco-editor";

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
				margin: "0, 10px, 0, 16px",
			}}
		>
			<Group
				orientation="horizontal"
				style={{ width: "100%", height: "100%" }}
			>
				<Panel defaultSize="35%" minSize="20%">
					<div
						style={{
							width: "100%",
							height: "100%",
							overflowY: "auto",
							border: "2px solid #5aa9e6",
							boxSizing: "border-box",
							backgroundColor: "#96CCFF8A",
							scrollbarWidth: "thin",
							scrollbarColor: "#5aa9e6 #96ccff8a",
						}}
					>
						<div
							style={{
								height: "800px",
								width: "850px",
								boxSizing: "border-box",
							}}
						>
							{/* TODO: Get task */}
							<span>
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! velit nobis odit possimus!
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! velit nobis odit possimus!
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! velit nobis odit possimus!
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! velit nobis odit possimus!
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! velit nobis odit possimus!
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! velit nobis odit possimus!
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! velit nobis odit possimus!
								Lorem ipsum dolor sit amet, consectetur
								adipisicing elit. Vel quae minus eligendi et
								quidem dolorum sapiente quod voluptates
								molestiae enim maiores ipsum praesentium,
								similique quos accusantium velit nobis odit
								possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus! Lorem ipsum dolor sit amet,
								consectetur adipisicing elit. Vel quae minus
								eligendi et quidem dolorum sapiente quod
								voluptates molestiae enim maiores ipsum
								praesentium, similique quos accusantium velit
								nobis odit possimus!
							</span>
						</div>
					</div>
				</Panel>
				<Separator
					style={{
						width: 2,
						background: "#93c5fd",
						cursor: "col-resize",
					}}
				/>
				<Panel minSize="30%">
					<div
						style={{
							width: "100%",
							height: "100%",
							border: "2px solid #5aa9e6",
						}}
					>
						<Editor
							className="editor"
							key={language}
							language={language}
							value={code}
							height={height}
							theme={theme}
							onChange={handelEditorChange}
						/>
					</div>
				</Panel>
			</Group>
		</div>
	);
};
