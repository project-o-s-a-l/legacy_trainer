import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { requestPasswordRecoveryCode } from "@/features/verificationCode/verificationCode";
import "../AuthProfileTheme.css";

export default function ForgotPassword() {
	const navigate = useNavigate();
	const [email, setEmail] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		if (!email.trim()) {
			setError("Enter the email linked to your account");
			return;
		}

		try {
			setError(null);
			setIsSubmitting(true);
			await requestPasswordRecoveryCode(email.trim());
			navigate("/confirm-email", {
				state: {
					email: email.trim(),
					flow: "recovery",
				},
			});
		} catch (error) {
			setError(
				error instanceof Error
					? error.message
					: "Unable to request password recovery code",
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
						<p className="auth-profile-panel-kicker">Recovery request</p>
						<h2 className="auth-profile-panel-title">
							Send verification code
						</h2>
					</div>

					<form className="auth-profile-form" onSubmit={handleSubmit}>
						<label className="auth-profile-field" htmlFor="forgot-email">
							<span className="auth-profile-label">Email</span>
							<input
								id="forgot-email"
								type="email"
								className="input auth-profile-input"
								placeholder="Enter your email"
								value={email}
								onChange={(event) => setEmail(event.target.value)}
								autoComplete="email"
								required
							/>
						</label>

						{error && (
							<p className="auth-profile-message auth-profile-message--error">
								{error}
							</p>
						)}

						<div className="auth-profile-actions">
							<Link className="auth-profile-link" to="/login">
								Back to login
							</Link>
							<button
								className="auth-profile-submit"
								type="submit"
								disabled={isSubmitting}
							>
								{isSubmitting ? "Sending..." : "Send code"}
							</button>
						</div>
					</form>
				</section>
			</section>
		</main>
	);
}
