import React, { useState } from "react";
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NavbarContext, useNavbar } from "@/shared/lib/layout/NavbarContext";

function TestConsumer() {
	const { isNavbarVisible, toggleNavbar } = useNavbar();

	return (
		<div>
			<span data-testid="navbar-state">
				{isNavbarVisible ? "Visible" : "Hidden"}
			</span>
			<button onClick={toggleNavbar}>Toggle Navbar</button>
		</div>
	);
}

function TestProviderWrapper() {
	const [isNavbarVisible, setNavbarVisible] = useState(true);

	const contextValue = () => {
		setNavbarVisible((prev) => !prev);
	};

	return (
		<NavbarContext.Provider
			value={{
				isNavbarVisible,
				setNavbarVisible,
				toggleNavbar: contextValue,
			}}
		>
			<TestConsumer />
		</NavbarContext.Provider>
	);
}

describe("useNavbar", () => {
	afterEach(() => {
		vi.resetAllMocks();
	});

	it("throws an error if used outside NavbarContext.Provider", () => {
		const consoleErrorSpy = vi
			.spyOn(console, "error")
			.mockImplementation(() => {});

		expect(() => render(<TestConsumer />)).toThrow(
			"useNavbar must be used inside NavbarContext.Provider",
		);

		consoleErrorSpy.mockRestore();
	});

	it("returns context value inside NavbarContext.Provider", () => {
		render(<TestProviderWrapper />);

		expect(screen.getByTestId("navbar-state")).toHaveTextContent("Visible");
	});

	it("toggles navbar state through context", async () => {
		const user = userEvent.setup();

		render(<TestProviderWrapper />);

		const state = screen.getByTestId("navbar-state");
		const button = screen.getByRole("button", { name: /toggle/i });

		expect(state).toHaveTextContent("Visible");

		await user.click(button);
		expect(state).toHaveTextContent("Hidden");

		await user.click(button);
		expect(state).toHaveTextContent("Visible");
	});
});
