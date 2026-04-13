import { useState } from "react";
import "./ChooseTask.css";
import { Button } from "@/shared";
import svgMatrix from "@/shared/assets/images/svg/matrix-static-dense-gray-transparent.svg";
import { useNavigate } from "react-router-dom";

export default function ChooseTask() {
	const [chooseShow, setChooseShow] = useState(false);
	const [chooseLanguage, setChooseLanguage] = useState("");
	const [chooseDificulty, setChooseDifficulty] = useState("");
	const navigate = useNavigate();

	return (
		<section className="choose-task-page">
			<img src={svgMatrix} alt="matrix" className="svg-choose-bg" />

			<div className="choose-top-row">
				<button
					onClick={() => setChooseShow((prev) => !prev)}
					className="btn-ghost btn-hide-chooses-task"
				>
					{chooseShow ? "v" : ">"}
				</button>

				<div className="choose-task-container">
					<div className="choose-task">
						<span className="choose-task-title">
							Choose a programming language
						</span>

						<ul
							className={`choose-task-options-list ${
								chooseShow ? "open" : "closed"
							}`}
						>
							<li onClick={() => setChooseLanguage("Python")}>
								Python
							</li>
							<li onClick={() => setChooseLanguage("C++")}>
								C++
							</li>
						</ul>
					</div>

					<div className="choose-task">
						<span className="choose-task-title">
							Difficulty level
						</span>

						<ul
							className={`choose-task-options-list ${
								chooseShow ? "open" : "closed"
							}`}
						>
							<li onClick={() => setChooseDifficulty("Easy")}>
								Easy
							</li>
							<li onClick={() => setChooseDifficulty("Medium")}>
								Medium
							</li>
							<li onClick={() => setChooseDifficulty("Hard")}>
								Hard
							</li>
						</ul>
					</div>
				</div>
			</div>

			<div className="choose-main-content">
				<div className="choose-left-column">
					<span className="span-get-task box-light">
						Get a task and start working
					</span>

					<div className="choose-logic-container">
						<span className="choose-logic-span">
							Chose: {chooseLanguage} {chooseDificulty}
						</span>
						<div className="choose-buttons-row">
							<Button
								className="chose-logic-btn"
								onClick={() => {
									if (chooseDificulty && chooseLanguage) {
										navigate("/CodeBlock", {
											state: {
												chooseLanguage,
												chooseDificulty,
											},
										});
									} else {
										alert("Please choose language and difficulty");
									}
								}}
							>
								Generate a task
							</Button>
							<Button
								className="chose-logic-btn"
								onClick={() => {
									setChooseLanguage("");
									setChooseDifficulty("");
								}}
							>
								Clear choose
							</Button>
						</div>
					</div>
				</div>
			</div>
		</section>
	);
}
