import { useState } from "react";
import "./Registration.css";
import { register_request } from "@/features/registr/registr-request";

function Registration() {
	const [username, setUsername] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		try {
			alert("Registration successful!");
			await register_request(username, email, password);
		} catch (error) {
			console.error(error);
		}
	};

	return (
		<div className="registration-page flex-center">
			<div className="registration-card card card-code-gradient ">
				<h1 className="registration-title">Registration</h1>

				<form
					className="registration-form flex-col"
					onSubmit={handleSubmit}
				>
					<label className="form-label">
						Username
						<input
							type="text"
							placeholder="Enter username"
							className="input form-input"
							onChange={(e) => setUsername(e.target.value)}
						/>
					</label>

					<label className="form-label">
						Email
						<input
							type="text"
							placeholder="Enter email"
							className="input form-input"
							onChange={(e) => setEmail(e.target.value)}
						/>
					</label>
					<label className="form-label">
						Password
						<input
							type="password"
							placeholder="Enter password"
							className="input form-input"
							onChange={(e) => setPassword(e.target.value)}
						/>
					</label>

					<label className="form-label">
						Confirm your password
						<input
							type="password"
							placeholder="Confirm your password"
							className="input form-input"
							onChange={(e) => {
								setConfirmPassword(e.target.value);
								if (confirmPassword !== password) {
									console.log("Incorrect password!");
								}
							}}
						/>
					</label>

					<button
						type="submit"
						className="btn-ghost btn-submit-registration"
					>
						Get code
					</button>
				</form>
			</div>
		</div>
	);
}
export default Registration;
