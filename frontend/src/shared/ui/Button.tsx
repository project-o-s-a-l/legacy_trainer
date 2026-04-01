import "./Button.css";

type ButtonProps = {
	children: React.ReactNode;
	variant?: "primary" | "secondary";
	type?: "button" | "submit" | "reset";
	className?: string;
	onClick?: () => void;
	disabled?: boolean;
};

export default function Button({
	children,
	type = "button",
	className = "",
	onClick,
	disabled = false,
}: ButtonProps) {
	return (
		<button
			type={type}
			className={`btn ${className}`}
			onClick={onClick}
			disabled={disabled}
		>
			{children}
		</button>
	);
}
