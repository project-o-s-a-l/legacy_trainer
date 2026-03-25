import { CodeBlock } from "./CodeBlock";

export default function CodeEditor() {
	const handleSubmit = (code: string) => console.log("Sumbit code: ", code);

	return (
		<>
			<h1>Code redactor:</h1>
			<CodeBlock
				language="typescript"
				defaultValue={`console.log('Hello World!');`}
				onChange={handleSubmit}
				height="800px"
				theme="#2196F3"
			/>

			<button onClick={() => handleSubmit("code")}>Run code</button>
		</>
	);
}
