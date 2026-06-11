import { useLocation, useNavigate } from "react-router-dom";
import { useNavbar } from "@/shared/index";
import { CodeBlock } from "./CodeBlock";
import "./CodeEditor.css";
import Button from "@/shared/ui/Button";
import { useRef, useState } from "react";
import { getScore } from "@/features/getScoreForSolution/getScoreForSolution";
import {
	checkSolution,
	type CheckSolutionProps,
} from "@/features/CheckSolution/CheckSolution";
import type { TaskResponse } from "@/features/getTask/getTask";

type LocationState = {
	chooseLanguage?: string;
	chooseDificulty?: string;
	task?: TaskResponse;
};

const languageMap: Record<string, string> = {
	Python: "python",
	"C++": "cpp",
};

// const defaultValues: Record<string, string> = {
// 	python: "def hello_python():\n\tprint('Hello, World!')",
// 	cpp: '#include <iostream>\n\nint main() {\n\tstd::cout << "Hello, World!";\n\treturn 0;\n}',
// };
export default function CodeEditor() {
	const nav = useNavigate();
	const { isNavbarVisible, toggleNavbar } = useNavbar();

	const location = useLocation();
	const { chooseLanguage, chooseDificulty, task } =
		(location.state as LocationState) || {};

	const RESULT_PANEL_MIN_HEIGHT = 56;
	const RESULT_PANEL_MAX_HEIGHT = 380;

	const monacoLanguage = chooseLanguage
		? languageMap[chooseLanguage] || task?.language || "plaintext"
		: task?.language || "plaintext";
	const defaultCode = task?.legacyCode ?? "";

	const [resultPanelHeight, setResultPanelHeight] = useState(
		RESULT_PANEL_MAX_HEIGHT,
	);
	const [isResultPanelDragging, setIsResultPanelDragging] = useState(false);
	const [isChecking, setIsChecking] = useState(false);
	const [isLoadingResult, setIsLoadingResult] = useState(false);
	const [checkResult, setCheckResult] = useState<CheckSolutionProps | null>(
		null,
	);

	const [code, setCode] = useState(defaultCode);

	const handleSubmit = async () => {
		if (!task) {
			const missingTaskResult: CheckSolutionProps = {
				submissionId: 0,
				taskId: 0,
				status: "error",
				score: 0,
				message: "Please choose a task before submitting a solution",
				testPassed: 0,
			};

			setCheckResult(missingTaskResult);
			setResultPanelHeight(RESULT_PANEL_MAX_HEIGHT);

			return null;
		}

		setIsChecking(true);
		setCheckResult(null);
		try {
			const result = await checkSolution(
				task.id,
				code,
				task.language || (chooseLanguage as string),
			);

			setCheckResult(result);
			setResultPanelHeight(RESULT_PANEL_MAX_HEIGHT);

			return result;
		} catch (error) {
			const result: CheckSolutionProps = {
				submissionId: 0,
				taskId: task.id,
				status: "failed",
				score: 0,
				message:
					error instanceof Error
						? error.message
						: "Не удалось проверить решение",
				testPassed: 0,
			};

			setCheckResult(result);
			setResultPanelHeight(RESULT_PANEL_MAX_HEIGHT);

			return null;
		} finally {
			setIsChecking(false);
		}
	};

	const resultPanelDragRef = useRef<{
		startY: number;
		startHeight: number;
	} | null>(null);

	const clamp = (value: number, min: number, max: number) => {
		return Math.min(Math.max(value, min), max);
	};

	const handleResultPanelPointerDown = (
		event: React.PointerEvent<HTMLDivElement>,
	) => {
		event.preventDefault();

		event.currentTarget.setPointerCapture(event.pointerId);

		resultPanelDragRef.current = {
			startY: event.clientY,
			startHeight: resultPanelHeight,
		};

		setIsResultPanelDragging(true);
	};

	const handleResultPanelPointerMove = (
		event: React.PointerEvent<HTMLDivElement>,
	) => {
		if (!resultPanelDragRef.current) {
			return;
		}

		const deltaY = resultPanelDragRef.current.startY - event.clientY;

		const nextHeight = clamp(
			resultPanelDragRef.current.startHeight + deltaY,
			RESULT_PANEL_MIN_HEIGHT,
			RESULT_PANEL_MAX_HEIGHT,
		);

		setResultPanelHeight(nextHeight);
	};

	const handleResultPanelPointerUp = (
		event: React.PointerEvent<HTMLDivElement>,
	) => {
		resultPanelDragRef.current = null;
		setIsResultPanelDragging(false);

		try {
			event.currentTarget.releasePointerCapture(event.pointerId);
		} catch {
			// Ignore release errors when the pointer capture is already cleared.
		}
	};

	return (
		<>
			<div className="code-editor-toolbar">
				<div className="code-editor-toolbar-spacer" aria-hidden="true" />
				<div className="code-editor-actions">
					<button
						type="button"
						className="btn btn-icon run-wrapper"
						onClick={() => handleSubmit()}
					>
						<svg className="btn-run-code" viewBox="0 0 128 128">
							<path
								d="  M52 42
									 Q52 36 58 40
									 L84 60
									 Q92 64 84 68
									 L58 88
									 Q52 92 52 86
									 Z"
								fill="currentColor"
							/>
						</svg>
					</button>
					<Button
						className="btn-check-solution"
						onClick={async () => {
							const result = await handleSubmit();

							if (!result || result.status !== "passed") {
								return;
							}

							try {
								setIsLoadingResult(true);
								const analysis = await getScore(result.submissionId);

								nav("/result", {
									state: {
										result: analysis,
										code,
										taskTitle: task?.title,
									},
								});
							} catch (error) {
								setCheckResult({
									submissionId: result.submissionId,
									taskId: result.taskId,
									status: "failed",
									score: 0,
									message:
										error instanceof Error
											? error.message
											: "Failed to load submission result",
									testPassed: result.testPassed,
								});
								setResultPanelHeight(RESULT_PANEL_MAX_HEIGHT);
							} finally {
								setIsLoadingResult(false);
							}
						}}
						disabled={isChecking || isLoadingResult}
					>
						{isChecking
							? "Checking..."
							: isLoadingResult
								? "Loading result..."
								: "Submit"}
					</Button>
				</div>
				<button
					type="button"
					onClick={toggleNavbar}
					className="btn-ghost btn-hide"
				>
					{isNavbarVisible ? "^" : "\u2228"}
				</button>
			</div>
			<div className="code-editor-meta">
				<span className="chosed-fields">
					Language: {chooseLanguage || task?.language || "not selected"}
					|Difficulty: {chooseDificulty || task?.difficulty || "not selected"}
				</span>
			</div>
			<CodeBlock
				language={monacoLanguage}
				defaultValue={defaultCode}
				onChange={(newCode) => setCode(newCode)}
				height="850px"
				theme="blueLight"
				task={{
					title: task?.title as string,
					description: task?.description as string,
				}}
			/>
			{checkResult && (
				<div
					className={`check-result-bar ${
						checkResult.status === "passed"
							? "check-result-bar-success"
							: "check-result-bar-error"
					} ${isResultPanelDragging ? "check-result-bar-dragging" : ""}`}
					style={{ height: `${resultPanelHeight}px` }}
				>
					<div
						className="check-result-top"
						onPointerDown={handleResultPanelPointerDown}
						onPointerMove={handleResultPanelPointerMove}
						onPointerUp={handleResultPanelPointerUp}
						onPointerCancel={handleResultPanelPointerUp}
					>
						<span className="check-result-title">
							{checkResult.status === "passed"
								? "Success"
								: "Error"}
						</span>
					</div>

					<div className="check-result-bar-content">
						<pre className="check-result-message">
							{checkResult.message}
						</pre>

						<div className="check-result-tests">
							Tests passed: {checkResult.testPassed} | Score:{" "}
							{checkResult.score}
						</div>
					</div>
				</div>
			)}
		</>
	);
}
