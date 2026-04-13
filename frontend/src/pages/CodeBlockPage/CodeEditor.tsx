import { useLocation } from "react-router-dom";
import { useNavbar } from "@/shared/index";
import { CodeBlock } from "./CodeBlock";
import "./CodeEditor.css";
import Button from "@/shared/ui/Button";
import { useEffect } from "react";

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
	const handleSubmit = (code: string) => console.log("Submit code: ", code);

	const { isNavbarVisible, toggleNavbar } = useNavbar();

	const location = useLocation();

	const { chooseLanguage, chooseDificulty } =
		(location.state as LocationState) || {};

	const monacoLanguage = chooseLanguage
		? languageMap[chooseLanguage] || "plaintext"
		: "plaintext";

	return (
		<>
			<div className="flex-between-center">
				<button
					type="button"
					className="btn btn-icon run-wrapper"
					onClick={() => handleSubmit("code")}
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
				{/* TODO: Check solution logic */}
				<Button className="btn-check-solution">Submit</Button>
				<button
					type="button"
					onClick={toggleNavbar}
					className="btn-ghost btn-hide"
				>
					{isNavbarVisible ? "^" : "\u2228"}
				</button>
			</div>
			<div className="flex">
				<span className="chosed-fields">Language: {chooseLanguage || "not selected"}|Difficulty: {chooseDificulty || "not selected"}</span>
			</div>
			<CodeBlock
				language={monacoLanguage}
				defaultValue={defaultValues[monacoLanguage] || ""}
				onChange={handleSubmit}
				height="850px"
				theme="blueLight"
			/>
		</>
	);
}
