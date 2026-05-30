import "./Button.css";

type ButtonProps = {
	children: React.ReactNode;
	variant?: "primary" | "secondary" | "ghost" | "icon";
	type?: "button" | "submit" | "reset";
	className?: string;
	onClick?: () => void;
	disabled?: boolean;
};

export default function Button({
	children,
	variant = "primary",
	type = "button",
	className = "",
	onClick,
	disabled = false,
}: ButtonProps) {
	return (
		<button
			type={type}
			className={`specific-btn specific-btn--${variant} ${className}`}
			onClick={onClick}
			disabled={disabled}
		>
			{children}
		</button>
	);
}
