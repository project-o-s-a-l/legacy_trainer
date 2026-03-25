import Editor from "@monaco-editor/react";
import React, { useState, useRef, useEffect } from "react";

type CodeBlockProps = {
	language?: string;
	defaultValue?: string;
	onChange?: (value: string) => void;
	height?: string | number;
	theme?: "light" | "vs-dark" | string;
};

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
					width: "850px",
					height: "800px",
					backgroundColor: "#96CCFF8A",
					flexShrink: 0,
				}}
			>
				<span>
					Lorem ipsum dolor sit amet, consectetur adipisicing elit.
					Vel quae minus eligendi et quidem dolorum sapiente quod
					voluptates molestiae enim maiores ipsum praesentium,
					similique quos accusantium velit nobis odit possimus! Lorem
					ipsum dolor sit amet, consectetur adipisicing elit. Vel quae
					minus eligendi et quidem dolorum sapiente quod voluptates
					molestiae enim maiores ipsum praesentium, similique quos
					accusantium velit nobis odit possimus! Lorem ipsum dolor sit
					amet, consectetur adipisicing elit. Vel quae minus eligendi
					et quidem dolorum sapiente quod voluptates molestiae enim
					maiores ipsum praesentium, similique quos accusantium velit
					nobis odit possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus! Lorem ipsum dolor sit amet, consectetur
					adipisicing elit. Vel quae minus eligendi et quidem dolorum
					sapiente quod voluptates molestiae enim maiores ipsum
					praesentium, similique quos accusantium velit nobis odit
					possimus!
				</span>
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
