import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Button from "./Button";

describe("Button", () => {
	it("renders with primary variant and button type by default", () => {
		render(<Button>Click me</Button>);

		const button = screen.getByRole("button", { name: "Click me" });

		expect(button).toHaveAttribute("type", "button");
		expect(button).toHaveClass("specific-btn", "specific-btn--primary");
	});

	it("applies custom props and calls the click handler", async () => {
		const user = userEvent.setup();
		const handleClick = vi.fn();

		render(
			<Button
				variant="ghost"
				type="submit"
				className="extra-class"
				onClick={handleClick}
			>
				Submit form
			</Button>,
		);

		const button = screen.getByRole("button", { name: "Submit form" });
		await user.click(button);

		expect(button).toHaveAttribute("type", "submit");
		expect(button).toHaveClass(
			"specific-btn",
			"specific-btn--ghost",
			"extra-class",
		);
		expect(handleClick).toHaveBeenCalledTimes(1);
	});

	it("stays disabled when requested", async () => {
		const user = userEvent.setup();
		const handleClick = vi.fn();

		render(
			<Button disabled onClick={handleClick}>
				Disabled action
			</Button>,
		);

		const button = screen.getByRole("button", { name: "Disabled action" });
		await user.click(button);

		expect(button).toBeDisabled();
		expect(handleClick).not.toHaveBeenCalled();
	});
});
