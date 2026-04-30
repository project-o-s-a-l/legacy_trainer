import Editor, { useMonaco } from "@monaco-editor/react";
import React, { useState, useEffect, useRef } from "react";
import type { CodeBlockProps } from "./model/types.ts";
import { BLUE_LIGHT_THEME_NAME, blueLightTheme } from "./lib/blueLightTheme.ts";
import { Group, Panel, Separator } from "react-resizable-panels";
import "./CodeBlock.css";
import { useLocation } from "react-router-dom";

export const CodeBlock: React.FC<CodeBlockProps> = ({
	language = "javascript",
	defaultValue = "",
	onChange,
	height = "800px",
	task,
}) => {
	const [code, setCode] = useState(defaultValue);
	const monaco = useMonaco();

	useEffect(() => {
		if (!monaco) return;

		monaco.editor.defineTheme(BLUE_LIGHT_THEME_NAME, blueLightTheme);
		monaco.editor.setTheme(BLUE_LIGHT_THEME_NAME);
	}, [monaco]);

	const handelEditorChange = (value: string | undefined) => {
		const newValue = value || "";
		setCode(newValue);
		onChange?.(newValue);
	};

	return (
		<div>
			<div className="main-code-editor-container">
				<Group orientation="horizontal" className="resizable-group">
					<Panel defaultSize="35%" minSize="20%">
						<div className="editor-panel">
							<div className="panel-header">
								<span className="panel-title">
									{task?.title}
								</span>
							</div>
							<div className="scroll-bar-container">
								<div className="task-container">
									<span>{task?.description}</span>
								</div>
							</div>
						</div>
					</Panel>
					<Separator className="separator" />
					<Panel minSize="30%">
						<div className="editor-panel">
							<div className="code-editor-container">
								<div className="panel-header">
									<span className="panel-title">
										Solution:
									</span>
								</div>
								<Editor
									className="editor"
									language={language}
									value={code}
									height={height}
									theme={BLUE_LIGHT_THEME_NAME}
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
