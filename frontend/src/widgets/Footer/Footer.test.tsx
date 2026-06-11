import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import Footer from "./Footer";

describe("Footer", () => {
	it("renders the project branding and footer copy", () => {
		render(<Footer />);

		expect(
			screen.getByAltText("logo Project O.S.A.L"),
		).toBeInTheDocument();
		expect(screen.getByText("LegacyTrainer")).toBeInTheDocument();
		expect(
			screen.getByText(
				"The project was created for educational and research purposes",
			),
		).toBeInTheDocument();
		expect(screen.getByText("Confidentiality")).toBeInTheDocument();
	});

	it("shows the current year in the copyright line", () => {
		render(<Footer />);

		expect(
			screen.getByText(`All rights reserved © ${new Date().getFullYear()}`),
		).toBeInTheDocument();
	});
});
