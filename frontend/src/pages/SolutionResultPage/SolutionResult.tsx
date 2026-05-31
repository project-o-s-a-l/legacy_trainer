import type { CSSProperties } from "react";
import "./SolutionResult.css";
import svgMatrix from "@/shared/assets/images/svg/matrix-static-dense-gray-transparent.svg";
import { Link, useLocation } from "react-router-dom";
import type { SolutionResultsProps } from "@/features/getScoreForSolution/getScoreForSolution";

type LocationState = {
	result?: SolutionResultsProps;
	code?: string;
	taskTitle?: string;
};

export default function SolutionResult() {
	const location = useLocation();
	const state = location.state as LocationState | null;
	const result = state?.result;
	const testsCheck = result?.checks.find((check) => check.checkType === "tests");
	const testDetails = testsCheck?.report.details ?? [];
	const avgScore = result?.overallScore ?? 0;

	const getPoints = () => {
		const score = Math.min(avgScore, 100);

		if (score > 1 && score < 20) {
			return 5;
		}

		return Math.floor(score / 20) * 20;
	};

	const scoreRingStyle = {
		"--score-percent": `${avgScore}%`,
	} as CSSProperties;

	if (!result) {
		return (
			<section className="solution-result-page">
				<div className="solution-empty-state card card-code-gradient">
					<h1>No submission result yet</h1>
					<p>
						Run and submit a task first, then this page will show the
						backend response for your solution.
					</p>
					<Link to="/ChooseTask" className="solution-empty-link">
						Go to task selection
					</Link>
				</div>
			</section>
		);
	}

	const scoreItems = [
		{ label: "Status", value: result.submission.status },
		{ label: "Tests passed", value: `${result.testsPassed}/${result.totalTests}` },
		{
			label: "Runtime",
			value:
				result.submission.executionTimeMs !== null
					? `${result.submission.executionTimeMs} ms`
					: "n/a",
		},
		{
			label: "Memory",
			value:
				result.submission.memoryUsedKb !== null
					? `${result.submission.memoryUsedKb} KB`
					: "n/a",
		},
	];

	return (
		<section className="solution-result-page">
			<div className="solution-result-layout">
				<div className="solution-left">
					<div className="solution-result-summary">
						<div className="score-ring" style={scoreRingStyle}>
							<span>{avgScore} %</span>
						</div>

						<div className="score-details">
							<p className="score-kicker">
								{state?.taskTitle || "Submission"} scored {avgScore} %
							</p>

							<ul className="score-list">
								{scoreItems.map((item) => (
									<li key={item.label}>
										<span>{item.label} </span>
										<strong>{item.value}</strong>
									</li>
								))}
							</ul>
						</div>
						<div className="solution-action">
							<span>{result.submission.language}</span>
							<span>
								Checked {result.submission.checkedAt ? "successfully" : "pending"}
							</span>
						</div>
					</div>

					<div className="result-message">
						<h1>
							You have been awarded {getPoints()} for this task
						</h1>
						<p className="result-supporting-copy">
							{result.failedTests === 0
								? "All available backend checks passed."
								: `${result.failedTests} test(s) still need attention.`}
						</p>

						{testDetails.length > 0 && (
							<ul className="result-test-list">
								{testDetails.map((detail) => (
									<li key={detail.name}>
										<span>{detail.name}</span>
										<strong>{detail.status}</strong>
									</li>
								))}
							</ul>
						)}
					</div>
				</div>

				<div className="code-preview-panel">
					<img src={svgMatrix} alt="" className="result-matrix-bg" />
					<div className="code-preview-header">
						<span>Submitted code</span>
						<span>#{result.submission.id}</span>
					</div>
					<pre aria-label="Solution preview">
						<code>{state?.code || "No code preview available"}</code>
					</pre>
				</div>
			</div>
		</section>
	);
}
