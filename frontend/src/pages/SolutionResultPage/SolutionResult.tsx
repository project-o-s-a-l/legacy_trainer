import type { CSSProperties } from "react";
import "./SolutionResult.css";
import svgMatrix from "@/shared/assets/images/svg/matrix-static-dense-gray-transparent.svg";
import { useLocation } from "react-router-dom";

type LocationState = {
	Architecture: number;
	CodeLogic: number;
	Standards: number;
};

const codePreview = `function validateUser(payload) {
  const errors = [];

  if (!payload.email || !payload.email.includes("@")) {
    errors.push("Invalid email");
  }

  if (payload.password.length < 8) {
    errors.push("Password is too short");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}`;

export default function SolutionResult() {
	const location = useLocation();
	const state = location.state as LocationState | null;

	const scoreItems = [
		{ label: "Architecture", value: state?.Architecture ?? 0 },
		{ label: "Code logic", value: state?.CodeLogic ?? 0 },
		{ label: "Standards", value: state?.Standards ?? 0 },
	];

	const avgScore = Math.round(
		scoreItems.reduce((sum, item) => sum + item.value, 0) /
			scoreItems.length,
	);

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
								Your code is {avgScore} % correct
							</p>

							<ul className="score-list">
								{scoreItems.map((item) => (
									<div key={item.label}>
										<span>{item.label} </span>
										<span>{item.value} %</span>
									</div>
								))}
							</ul>
						</div>
						{/*TODO: Feature func*/}
						{/* <div className="solution-action">
							<button className="solution-link">
								AI Analysis
							</button>
							<span>Learn more about errors</span>
						</div> */}
					</div>

					<div className="result-message">
						<h1>
							You have been awarded {getPoints()} for this task
						</h1>
					</div>
				</div>

				<div className="code-preview-panel">
					<img src={svgMatrix} alt="" className="result-matrix-bg" />
					<pre aria-label="Solution preview">
						<code>{codePreview}</code>
					</pre>
				</div>
			</div>
		</section>
	);
}
