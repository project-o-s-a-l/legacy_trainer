import { useState, type FormEvent } from "react";
import "../AuthProfileTheme.css";
import { register_request } from "@/features/registr/registr-request";
import { requestRegistrationVerificationCode } from "@/features/verificationCode/verificationCode";
import { Link, useNavigate } from "react-router-dom";

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
		<main className="auth-profile-page">
			<section className="auth-profile-shell auth-profile-shell--single">
				<section className="auth-profile-card auth-profile-form-panel auth-profile-form-panel--single">
					<div className="auth-profile-form-header">
						<p className="auth-profile-panel-kicker">Account details</p>
						<h2 className="auth-profile-panel-title">Registration</h2>
					</div>

					<form className="auth-profile-form" onSubmit={handleSubmit}>
						<div className="auth-profile-row">
							<label className="auth-profile-field">
								<span className="auth-profile-label">Username</span>
								<input
									type="text"
									placeholder="Enter username"
									className="input auth-profile-input"
									value={username}
									onChange={(e) => setUsername(e.target.value)}
									required
								/>
							</label>

							<label className="auth-profile-field">
								<span className="auth-profile-label">Email</span>
								<input
									type="email"
									placeholder="Enter email"
									className="input auth-profile-input"
									value={email}
									onChange={(e) => setEmail(e.target.value)}
									required
								/>
							</label>
						</div>

						<div className="auth-profile-row">
							<label className="auth-profile-field">
								<span className="auth-profile-label">Password</span>
								<input
									type="password"
									placeholder="Enter password"
									className="input auth-profile-input"
									value={password}
									onChange={(e) => setPassword(e.target.value)}
									required
								/>
							</label>

							<label className="auth-profile-field">
								<span className="auth-profile-label">Confirm password</span>
								<input
									type="password"
									placeholder="Confirm your password"
									className="input auth-profile-input"
									value={confirmPassword}
									onChange={(e) => setConfirmPassword(e.target.value)}
									required
								/>
							</label>
						</div>

						{error && (
							<p className="auth-profile-message auth-profile-message--error">
								{error}
							</p>
						)}

						<div className="auth-profile-actions">
							<Link className="auth-profile-link" to="/login">
								Already have an account?
							</Link>
							<button
								type="submit"
								className="auth-profile-submit"
								disabled={isSubmitting}
							>
								{isSubmitting ? "Sending code..." : "Get code"}
							</button>
						</div>
					</form>
				</section>
			</section>
		</main>
	);
}
export default Registration;
