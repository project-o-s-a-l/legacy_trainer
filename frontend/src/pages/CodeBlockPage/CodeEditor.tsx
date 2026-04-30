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

type LocationState = {
	chooseLanguage?: string;
	chooseDificulty?: string;
};


const languageMap: Record<string, string> = {
	Python: "python",
	"C++": "cpp",
};

const defaultValues: Record<string, string> = {
	python: "def hello_python():\n\tprint('Hello, World!')",
	cpp: '#include <iostream>\n\nint main() {\n\tstd::cout << "Hello, World!";\n\treturn 0;\n}',
};
export default function CodeEditor() {
	const nav = useNavigate();
	const { isNavbarVisible, toggleNavbar } = useNavbar();

	const location = useLocation();
	const { chooseLanguage, chooseDificulty } =
		(location.state as LocationState) || {};

	const RESULT_PANEL_MIN_HEIGHT = 56;
	const RESULT_PANEL_MAX_HEIGHT = 380;

	const monacoLanguage = chooseLanguage
		? languageMap[chooseLanguage] || "plaintext"
		: "plaintext";
	const defaultCode = defaultValues[monacoLanguage] || "";

	const [resultPanelHeight, setResultPanelHeight] = useState(
		RESULT_PANEL_MAX_HEIGHT,
	);
	const [isResultPanelDragging, setIsResultPanelDragging] = useState(false);
	const [isChecking, setIsChecking] = useState(false);
	const [checkResult, setCheckResult] = useState<CheckSolutionProps | null>(
		null,
	);

	const [code, setCode] = useState(defaultCode);

	const handleSubmit = async () => {
		setIsChecking(true);
		setCheckResult(null);

		try {
			const result = await checkSolution(
				code,
				chooseLanguage as string,
				chooseDificulty as string,
			);

			setCheckResult(result);
			setResultPanelHeight(RESULT_PANEL_MAX_HEIGHT);

			return result;
		} catch (error) {
			const result: CheckSolutionProps = {
				ok: false,
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
		} catch {}
	};

	return (
		<>
			<div className="flex-between-center">
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

						if (!result || !result.ok) {
							return;
						}

						const analysis = await getScore();

						nav("/result", {
							state: {
								Architecture: analysis.Architecture,
								CodeLogic: analysis.CodeLogic,
								Standards: analysis.Standards,
							},
						});
					}}
					disabled={isChecking}
				>
					{isChecking ? "Checking..." : "Submit"}
				</Button>
				<button
					type="button"
					onClick={toggleNavbar}
					className="btn-ghost btn-hide"
				>
					{isNavbarVisible ? "^" : "\u2228"}
				</button>
			</div>
			<div className="flex">
				<span className="chosed-fields">
					Language: {chooseLanguage || "not selected"}|Difficulty:{" "}
					{chooseDificulty || "not selected"}
				</span>
			</div>
			<CodeBlock
				language={monacoLanguage}
				defaultValue={defaultCode}
				onChange={(newCode) => setCode(newCode)}
				height="850px"
				theme="blueLight"
			/>
			{checkResult && (
				<div
					className={`check-result-bar ${
						checkResult.ok
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
							{checkResult.ok ? "Success" : "Error"}
						</span>
					</div>

					<div className="check-result-bar-content">
						<pre className="check-result-message">
							{checkResult.message}
						</pre>

						<div className="check-result-tests">
							Tests passed: {checkResult.testPassed}
						</div>
					</div>
				</div>
			)}
		</>
	);
}
