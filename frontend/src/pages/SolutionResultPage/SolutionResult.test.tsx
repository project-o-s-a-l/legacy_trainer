import { describe, it, expect } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import SolutionResult from "./SolutionResult";
import type { SolutionResultsProps } from "@/features/getScoreForSolution/getScoreForSolution";

type LocationState = {
	result?: SolutionResultsProps;
	code?: string;
	taskTitle?: string;
};

function createResult(overallScore = 90): SolutionResultsProps {
	return {
		submission: {
			id: 73,
			taskId: 42,
			userId: 7,
			language: "typescript",
			status: "passed",
			score: overallScore,
			submittedAt: "2026-06-09T12:00:00.000Z",
			checkedAt: "2026-06-09T12:00:05.000Z",
			memoryUsedKb: 128,
			executionTimeMs: 42,
		},
		checks: [
			{
				id: 1,
				checkType: "tests",
				status: "passed",
				score: overallScore,
				report: {
					total: 10,
					passed: 9,
					failed: 1,
					details: [
						{ name: "test_valid_user", status: "passed" },
						{ name: "test_invalid_user", status: "failed" },
					],
				},
				createdAt: "2026-06-09T12:00:05.000Z",
			},
		],
		totalTests: 10,
		testsPassed: 9,
		failedTests: 1,
		overallScore,
	};
}

function renderComponent(state: LocationState | null = {
	result: createResult(),
	code: "function validateUser(user) { return Boolean(user); }",
	taskTitle: "Transform Metrics",
}) {
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
			result: createResult(90),
			taskTitle: "Transform Metrics",
		});

		const scoreRing = container.querySelector(".score-ring");

		expect(scoreRing).toBeInTheDocument();
		expect(
			within(scoreRing as HTMLElement).getByText("90 %"),
		).toBeInTheDocument();
		expect(
			screen.getByText("Transform Metrics scored 90 %"),
		).toBeInTheDocument();
	});

	it("render submission summary items", () => {
		const { container } = renderComponent({
			result: createResult(90),
		});

		const scoreList = container.querySelector(".score-list");

		expect(scoreList).toBeInTheDocument();

		const scoreListQueries = within(scoreList as HTMLElement);

		expect(scoreListQueries.getByText("Status")).toBeInTheDocument();
		expect(scoreListQueries.getByText("Tests passed")).toBeInTheDocument();
		expect(scoreListQueries.getByText("Runtime")).toBeInTheDocument();
		expect(scoreListQueries.getByText("Memory")).toBeInTheDocument();

		expect(scoreListQueries.getByText("passed")).toBeInTheDocument();
		expect(scoreListQueries.getByText("9/10")).toBeInTheDocument();
		expect(scoreListQueries.getByText("42 ms")).toBeInTheDocument();
		expect(scoreListQueries.getByText("128 KB")).toBeInTheDocument();
	});

	it("sets CSS variable --score-percent equal to average score", () => {
		const { container } = renderComponent({
			result: createResult(80),
		});

		const scoreRing = container.querySelector(".score-ring");

		expect(scoreRing).toBeInTheDocument();
		expect(scoreRing).toHaveStyle({
			"--score-percent": "80%",
		});
	});

	it("show submission score from backend", () => {
	renderComponent({
		result: createResult(90),
	});

	    expect(
	    	screen.getByText("You have been awarded 90 for this task"),
	    ).toBeInTheDocument();
    });

	it("show 100 points when backend submission score is 100", () => {
		renderComponent({
			result: createResult(100),
		});

		expect(
			screen.getByText("You have been awarded 100 for this task"),
		).toBeInTheDocument();
	});

	it("show low backend score without custom frontend rounding", () => {
	renderComponent({
		result: createResult(10),
	});

	    expect(
		    screen.getByText("You have been awarded 10 for this task"),
	    ).toBeInTheDocument();
    });

	it("show empty state, if location.state is null", () => {
		renderComponent(null);

		expect(screen.getByText("No submission result yet")).toBeInTheDocument();
		expect(
			screen.getByText(
				"Run and submit a task first, then this page will show the backend response for your solution.",
			),
		).toBeInTheDocument();
		expect(
			screen.getByRole("link", { name: "Go to task selection" }),
		).toHaveAttribute("href", "/ChooseTask");
	});

	it("render code preview", () => {
		renderComponent({
			result: createResult(95),
			code: "function validateUser(user) { return Boolean(user); }",
		});

		expect(screen.getByLabelText("Solution preview")).toBeInTheDocument();
		expect(screen.getByText(/function validateUser/)).toBeInTheDocument();
	});
});
