import { useState, type KeyboardEvent } from "react";
import "./ChooseTask.css";
import { Button } from "@/shared";
import svgMatrix from "@/shared/assets/images/svg/matrix-static-dense-gray-transparent.svg";
import { useNavigate } from "react-router-dom";
import { getTask } from "@/features/getTask/getTask";

export default function ChooseTask() {
	const [chooseShow, setChooseShow] = useState(false);
	const [chooseLanguage, setChooseLanguage] = useState("");
	const [chooseDificulty, setChooseDifficulty] = useState("");
	const navigate = useNavigate();

	const toggleChooseShow = () => setChooseShow((prev) => !prev);

	const handleChooseKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
		if (event.target !== event.currentTarget) {
			return;
		}

		if (event.key !== "Enter" && event.key !== " ") {
			return;
		}

		event.preventDefault();
		toggleChooseShow();
	};

	const getOptionClassName = (isSelected: boolean) =>
		`choose-task-option${
			isSelected ? " choose-task-option--selected" : ""
		}`;

	return (
		<section className="choose-task-page">
			<img src={svgMatrix} alt="matrix" className="svg-choose-bg" />

			<div
				className="choose-top-row"
				role="button"
				tabIndex={0}
				aria-expanded={chooseShow}
				aria-label="Toggle task filters"
				onClick={toggleChooseShow}
				onKeyDown={handleChooseKeyDown}
			>
				<span
					className="btn-ghost btn-hide-chooses-task"
					aria-hidden="true"
				>
					{chooseShow ? "v" : ">"}
				</span>

				<div className="choose-task-container">
					<div className="choose-task">
						<span className="choose-task-title">
							Choose a programming language
						</span>

						<div
							className={`choose-task-options-shell ${
								chooseShow ? "open" : "closed"
							}`}
							aria-hidden={!chooseShow}
						>
							<ul className="choose-task-options-list">
								<li>
									<button
										type="button"
										className={getOptionClassName(
											chooseLanguage === "Python",
										)}
										aria-pressed={chooseLanguage === "Python"}
										tabIndex={chooseShow ? 0 : -1}
										onClick={(event) => {
											event.stopPropagation();
											setChooseLanguage("Python");
										}}
									>
										Python
									</button>
								</li>
								<li>
									<button
										type="button"
										className={getOptionClassName(
											chooseLanguage === "C++",
										)}
										aria-pressed={chooseLanguage === "C++"}
										tabIndex={chooseShow ? 0 : -1}
										onClick={(event) => {
											event.stopPropagation();
											setChooseLanguage("C++");
										}}
									>
										C++
									</button>
								</li>
							</ul>
						</div>
					</div>

					<div className="choose-task">
						<span className="choose-task-title">
							Difficulty level
						</span>

						<div
							className={`choose-task-options-shell ${
								chooseShow ? "open" : "closed"
							}`}
							aria-hidden={!chooseShow}
						>
							<ul className="choose-task-options-list">
								<li>
									<button
										type="button"
										className={getOptionClassName(
											chooseDificulty === "Easy",
										)}
										aria-pressed={chooseDificulty === "Easy"}
										tabIndex={chooseShow ? 0 : -1}
										onClick={(event) => {
											event.stopPropagation();
											setChooseDifficulty("Easy");
										}}
									>
										Easy
									</button>
								</li>
								<li>
									<button
										type="button"
										className={getOptionClassName(
											chooseDificulty === "Medium",
										)}
										aria-pressed={chooseDificulty === "Medium"}
										tabIndex={chooseShow ? 0 : -1}
										onClick={(event) => {
											event.stopPropagation();
											setChooseDifficulty("Medium");
										}}
									>
										Medium
									</button>
								</li>
								<li>
									<button
										type="button"
										className={getOptionClassName(
											chooseDificulty === "Hard",
										)}
										aria-pressed={chooseDificulty === "Hard"}
										tabIndex={chooseShow ? 0 : -1}
										onClick={(event) => {
											event.stopPropagation();
											setChooseDifficulty("Hard");
										}}
									>
										Hard
									</button>
								</li>
							</ul>
						</div>
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
								onClick={async () => {
									if (!chooseDificulty || !chooseLanguage) {
										alert("Please choose language and difficulty");
										return;
									}

									try {
										const task = await getTask(
											chooseLanguage,
											chooseDificulty,
										);

										navigate("/CodeBlock", {
											state: {
												chooseLanguage,
												chooseDificulty,
												task,
											},
										});
									} catch (error) {
										alert(
											error instanceof Error
												? error.message
												: "Failed to get task",
										);
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
