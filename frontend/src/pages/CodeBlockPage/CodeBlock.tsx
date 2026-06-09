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
	task,
}) => {
	const [code, setCode] = useState(defaultValue);
	const [isCompactLayout, setIsCompactLayout] = useState<boolean>(() =>
		typeof window !== "undefined" ? window.innerWidth <= 1180 : false,
	);
	const monaco = useMonaco();

	useEffect(() => {
		if (!monaco) return;

		monaco.editor.defineTheme(BLUE_LIGHT_THEME_NAME, blueLightTheme);
		monaco.editor.setTheme(BLUE_LIGHT_THEME_NAME);
	}, [monaco]);

	useEffect(() => {
		if (typeof window === "undefined") {
			return;
		}

		const mediaQuery = window.matchMedia("(max-width: 1180px)");
		const updateLayout = () => setIsCompactLayout(mediaQuery.matches);

		updateLayout();

		mediaQuery.addEventListener("change", updateLayout);

		return () => {
			mediaQuery.removeEventListener("change", updateLayout);
		};
	}, []);

	const handelEditorChange = (value: string | undefined) => {
		const newValue = value || "";
		setCode(newValue);
		onChange?.(newValue);
	};

	const groupOrientation = isCompactLayout ? "vertical" : "horizontal";
	const editorHeight = isCompactLayout ? "640px" : height;

	return (
		<div>
			<div
				className={`main-code-editor-container ${
					isCompactLayout ? "main-code-editor-container--stacked" : ""
				}`}
			>
				<Group orientation={groupOrientation} className="resizable-group">
					<Panel defaultSize={isCompactLayout ? 38 : 35} minSize={25}>
						<div className="editor-panel">
							<div className="panel-header">
								<span className="panel-title">
									{task?.title}
								</span>
							</div>
							<div className="scroll-bar-container">
								<div
									className={`task-container ${
										isCompactLayout ? "task-container--stacked" : ""
									}`}
								>
									<span>{task?.description}</span>
								</div>
							</div>
						</div>
					</Panel>
					<Separator
						className={`separator ${
							isCompactLayout ? "separator-vertical" : "separator-horizontal"
						}`}
					/>
					<Panel minSize={30}>
						<div className="editor-panel">
							<div
								className={`code-editor-container ${
									isCompactLayout ? "code-editor-container--stacked" : ""
								}`}
							>
								<div className="panel-header">
									<span className="panel-title">
										Solution:
									</span>
								</div>
								<Editor
									className="editor"
									language={language}
									value={code}
									height={editorHeight}
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
