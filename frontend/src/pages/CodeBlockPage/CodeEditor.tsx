import { useNavbar } from "@/shared/lib/layout/NavbarContext";
import { CodeBlock } from "./CodeBlock";
import "./CodeEditor.css";
import Button from "@/shared/ui/Button";

export default function CodeEditor() {
	const handleSubmit = (code: string) => console.log("Submit code: ", code);

	const { isNavbarVisible, toggleNavbar } = useNavbar();

	return (
		<>
			<button
				type="button"
				onClick={toggleNavbar}
				className="flex-right btn-ghost btn-hide"
			>
				{isNavbarVisible ? "^" : "\u2228"}
			</button>

			<div className="btn-submit-container flex-center">
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
				{/* <button className="btn-check-solution">Submit</button> */}
			</div>
			<CodeBlock
				language="typescript"
				defaultValue={`console.log('Hello World!');`}
				onChange={handleSubmit}
				height="850px"
				theme="blueLight"
			/>
		</>
	);
}
