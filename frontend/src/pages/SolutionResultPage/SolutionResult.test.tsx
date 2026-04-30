import { describe, it, expect } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import SolutionResult from "./SolutionResult";

type LocationState = {
	Architecture: number;
	CodeLogic: number;
	Standards: number;
};

function renderComponent(state: LocationState | null = null) {
	return render(
		<MemoryRouter
			initialEntries={[
				{
					pathname: "/result",
					state,
				},
			]}
		>
			<SolutionResult />
		</MemoryRouter>,
	);
}

describe("SolutionResult", () => {
	it("render average score from location.state", () => {
		const { container } = renderComponent({
			Architecture: 80,
			CodeLogic: 90,
			Standards: 100,
		});

		const scoreRing = container.querySelector(".score-ring");

		expect(scoreRing).toBeInTheDocument();

		expect(
			within(scoreRing as HTMLElement).getByText("90 %"),
		).toBeInTheDocument();

		expect(
			screen.getByText("Your code is 90 % correct"),
		).toBeInTheDocument();
	});

	it("render mark for each category", () => {
		const { container } = renderComponent({
			Architecture: 70,
			CodeLogic: 80,
			Standards: 90,
		});

		const scoreList = container.querySelector(".score-list");

		expect(scoreList).toBeInTheDocument();

		const scoreListQueries = within(scoreList as HTMLElement);

		expect(scoreListQueries.getByText("Architecture")).toBeInTheDocument();
		expect(scoreListQueries.getByText("Code logic")).toBeInTheDocument();
		expect(scoreListQueries.getByText("Standards")).toBeInTheDocument();

		expect(scoreListQueries.getByText("70 %")).toBeInTheDocument();
		expect(scoreListQueries.getByText("80 %")).toBeInTheDocument();
		expect(scoreListQueries.getByText("90 %")).toBeInTheDocument();
	});

	it("sets CSS variable --score-percent equal to average score", () => {
		const { container } = renderComponent({
			Architecture: 60,
			CodeLogic: 80,
			Standards: 100,
		});

		const scoreRing = container.querySelector(".score-ring");

		expect(scoreRing).toBeInTheDocument();
		expect(scoreRing).toHaveStyle({
			"--score-percent": "80%",
		});
	});

	it("show 80 points, if average score is 90", () => {
		renderComponent({
			Architecture: 80,
			CodeLogic: 90,
			Standards: 100,
		});

		expect(
			screen.getByText("You have been awarded 80 for this task"),
		).toBeInTheDocument();
	});

	it("show 100 points, if average score is 100", () => {
		renderComponent({
			Architecture: 100,
			CodeLogic: 100,
			Standards: 100,
		});

		expect(
			screen.getByText("You have been awarded 100 for this task"),
		).toBeInTheDocument();
	});

	it("show 5 points, if average score is greater than 1 and less than 20", () => {
		renderComponent({
			Architecture: 10,
			CodeLogic: 15,
			Standards: 20,
		});

		expect(
			screen.getByText("You have been awarded 5 for this task"),
		).toBeInTheDocument();
	});

	it("show 0, if location.state is null", () => {
		const { container } = renderComponent(null);

		const scoreRing = container.querySelector(".score-ring");
		const scoreList = container.querySelector(".score-list");

		expect(scoreRing).toBeInTheDocument();
		expect(scoreList).toBeInTheDocument();

		expect(
			within(scoreRing as HTMLElement).getByText("0 %"),
		).toBeInTheDocument();

		expect(
			screen.getByText("Your code is 0 % correct"),
		).toBeInTheDocument();

		expect(
			within(scoreList as HTMLElement).getAllByText("0 %"),
		).toHaveLength(3);

		expect(
			screen.getByText("You have been awarded 0 for this task"),
		).toBeInTheDocument();
	});

	it("render AI Analysis button", () => {
		renderComponent({
			Architecture: 75,
			CodeLogic: 85,
			Standards: 95,
		});

		expect(
			screen.getByRole("button", { name: "AI Analysis" }),
		).toBeInTheDocument();
	});

	it("render code preview", () => {
		renderComponent({
			Architecture: 75,
			CodeLogic: 85,
			Standards: 95,
		});

		expect(screen.getByLabelText("Solution preview")).toBeInTheDocument();

		expect(screen.getByText(/function validateUser/)).toBeInTheDocument();
	});
});
