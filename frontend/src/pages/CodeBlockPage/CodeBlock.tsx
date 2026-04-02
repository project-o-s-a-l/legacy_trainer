import Editor, { useMonaco } from "@monaco-editor/react";
import React, { useState, useEffect } from "react";
import type { CodeBlockProps } from "./model/types.ts";
import { BLUE_LIGHT_THEME_NAME, blueLightTheme } from "./lib/blueLightTheme.ts";
import { Group, Panel, Separator } from "react-resizable-panels";
import "./CodeBlock.css";

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
		<div>
			<div className="main-code-editor-container">
				<Group orientation="horizontal" className="resizable-group">
					<Panel defaultSize="35%" minSize="20%">
						<div className="editor-panel">
							<div className="panel-header">
								<span className="panel-title">Problem:</span>
							</div>
							<div className="scroll-bar-container">
								<div className="task-container">
									{/* TODO: Get task */}
									<span>
										Lorem ipsum dolor sit amet, consectetur
										adipisicing elit. Vel quae minus
										eligendi et quidem dolorum sapiente quod
										voluptates molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! velit nobis
										odit possimus! Lorem ipsum dolor sit
										amet, consectetur adipisicing elit. Vel
										quae minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! velit nobis odit possimus!
										Lorem ipsum dolor sit amet, consectetur
										adipisicing elit. Vel quae minus
										eligendi et quidem dolorum sapiente quod
										voluptates molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! velit nobis
										odit possimus! Lorem ipsum dolor sit
										amet, consectetur adipisicing elit. Vel
										quae minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! velit nobis odit possimus!
										Lorem ipsum dolor sit amet, consectetur
										adipisicing elit. Vel quae minus
										eligendi et quidem dolorum sapiente quod
										voluptates molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! velit nobis
										odit possimus! Lorem ipsum dolor sit
										amet, consectetur adipisicing elit. Vel
										quae minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! velit nobis odit possimus!
										Lorem ipsum dolor sit amet, consectetur
										adipisicing elit. Vel quae minus
										eligendi et quidem dolorum sapiente quod
										voluptates molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! Lorem ipsum
										dolor sit amet, consectetur adipisicing
										elit. Vel quae minus eligendi et quidem
										dolorum sapiente quod voluptates
										molestiae enim maiores ipsum
										praesentium, similique quos accusantium
										velit nobis odit possimus! velit nobis
										odit possimus! Lorem ipsum dolor sit
										amet, consectetur adipisicing elit. Vel
										quae minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus! Lorem ipsum dolor sit amet,
										consectetur adipisicing elit. Vel quae
										minus eligendi et quidem dolorum
										sapiente quod voluptates molestiae enim
										maiores ipsum praesentium, similique
										quos accusantium velit nobis odit
										possimus!
									</span>
								</div>
							</div>
						</div>
					</Panel>
					<Separator className="separator" />
					<Panel minSize="30%">
						<div className="editor-panel">
							<div className="code-editor-container">
								<div className="panel-header">
									<span className="panel-title">Solution:</span>
								</div>
								<Editor
									className="editor"
									key={language}
									language={language}
									value={code}
									height={height}
									theme={theme}
									onChange={handelEditorChange}
									options={{
										minimap: { enabled: false },
										wordWrap: "on",
										scrollBeyondLastLine: false,
										scrollbar: {
											horizontal: "hidden",
											horizontalScrollbarSize: 0,
											useShadows: false,
										},
									}}
								/>
							</div>
						</div>
					</Panel>
				</Group>
			</div>
		</div>
	);
};
