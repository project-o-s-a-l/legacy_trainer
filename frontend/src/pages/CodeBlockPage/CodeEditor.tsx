import { useLocation, useNavigate } from "react-router-dom";
import { useNavbar } from "@/shared/index";
import { CodeBlock } from "./CodeBlock";
import "./CodeEditor.css";
import Button from "@/shared/ui/Button";
import { useEffect, useState } from "react";
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
	const location = useLocation();

	const [data, setData] = useState<CheckSolutionProps | null>(null);

	const { chooseLanguage, chooseDificulty } =
		(location.state as LocationState) || {};

	const monacoLanguage = chooseLanguage
		? languageMap[chooseLanguage] || "plaintext"
		: "plaintext";

	const defaultCode = defaultValues[monacoLanguage] || "";
	const [code, setCode] = useState(defaultCode);

	const handleSubmit = async () => {
		console.log("Submit code: ", code);
		const data = await checkSolution(
			code,
			chooseLanguage as string,
			chooseDificulty as string,
		);
		setData(data);
	};
	const nav = useNavigate();
	const { isNavbarVisible, toggleNavbar } = useNavbar();

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
						const analysis = await getScore();
						handleSubmit();
						if(data === null)
							return

						if (data.ok) {
							nav("/result", {
								state: {
									Architecture: analysis.Architecture,
									CodeLogic: analysis.CodeLogic,
									Standards: analysis.Standards,
								},
							});
						}
					}}
				>
					Submit
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
		</>
	);
}
