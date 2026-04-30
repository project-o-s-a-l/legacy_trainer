export type CodeBlockProps = {
	language?: string;
	defaultValue?: string;
	onChange?: (value: string) => void;
	height?: string | number;
	theme?: "light" | "vs-dark" | string;
	task?: {
		title: string;
		description: string;
	};
};