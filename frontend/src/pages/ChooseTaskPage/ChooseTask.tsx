import { useState } from "react";
import "./ChooseTask.css";
import { Button } from "@/shared";
import svgMatrix from "@/shared/assets/images/svg/matrix-static-dense-gray-transparent.svg";

export default function ChooseTask() {
	const [chooseShow, setChooseShow] = useState(false);

	return (
		<section className="choose-task-page">
			<img src={svgMatrix} alt="matrix" className="svg-choose-bg" />

			<div className="choose-top-row">
				<button className="btn-ghost btn-hide-chooses-task">
					&gt;
				</button>
				<span className="choose-task">
					Choose a programming language
				</span>
				<span className="choose-task">Difficulty level</span>
			</div>

			<div className="choose-main-content">
				<div className="choose-left-column">
					<span className="span-get-task box-light">
						Get a task and start working
					</span>

					<div className="choose-logic-container">
						<span className="choose-logic-span">Chose:</span>
						<Button className="chose-logic-btn">Generate a task</Button>
					</div>
				</div>
			</div>
		</section>
	);
}
