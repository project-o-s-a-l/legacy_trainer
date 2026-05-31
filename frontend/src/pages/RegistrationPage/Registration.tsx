import { useState, type FormEvent } from "react";
import "./Registration.css";
import { register_request } from "@/features/registr/registr-request";
import { requestRegistrationVerificationCode } from "@/features/verificationCode/verificationCode";
import { useNavigate } from "react-router-dom";

function Registration() {
	const navigate = useNavigate();
	const [username, setUsername] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
		e.preventDefault();

		if (password !== confirmPassword) {
			setError("Passwords do not match");
			return;
		}

		try {
			setError(null);
			setIsSubmitting(true);

			const response = await register_request(username, email, password);
			await requestRegistrationVerificationCode(response.user.email);

			navigate("/confirm-email", {
				state: {
					email: response.user.email,
					flow: "registration",
				},
			});
		} catch (error) {
			console.error(error);
			setError(
				error instanceof Error
					? error.message
					: "Registration failed",
			);
		} finally {
			setIsSubmitting(false);
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
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							required
						/>
					</label>

					<label className="form-label">
						Email
						<input
							type="email"
							placeholder="Enter email"
							className="input form-input"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							required
						/>
					</label>
					<label className="form-label">
						Password
						<input
							type="password"
							placeholder="Enter password"
							className="input form-input"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
						/>
					</label>

					<label className="form-label">
						Confirm your password
						<input
							type="password"
							placeholder="Confirm your password"
							className="input form-input"
							value={confirmPassword}
							onChange={(e) => setConfirmPassword(e.target.value)}
							required
						/>
					</label>

					{error && <p className="registration-error">{error}</p>}

					<button
						type="submit"
						className="btn-ghost btn-submit-registration"
						disabled={isSubmitting}
					>
						{isSubmitting ? "Sending code..." : "Get code"}
					</button>
				</form>
			</div>
		</div>
	);
}
export default Registration;
