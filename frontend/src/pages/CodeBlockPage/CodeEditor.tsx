import { CodeBlock } from "./CodeBlock";

export default function CodeEditor() {
	const handleSubmit = (code: string) => console.log("Sumbit code: ", code);

	return (
		<>
			
			<CodeBlock
				language="typescript"
				defaultValue={`console.log('Hello World!');`}
				onChange={handleSubmit}
				height="800px"
				theme="blueLight"
			/>

			<button onClick={() => handleSubmit("code")}>Run code</button>
		</>
	);
}
