import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "@/shared/ui/Button";
import { requestPasswordRecoveryCode } from "@/features/verificationCode/verificationCode";
import "./ForgotPassword.css";

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
		<main className="forgot-password-page">
			<section className="forgot-password-shell card card-code-gradient">
				<div className="forgot-password-copy">
					<p className="forgot-password-kicker">Password recovery</p>
					<h1 className="forgot-password-title">Forgot your password?</h1>
					<p className="forgot-password-text">
						Enter your email and continue with the verification code
						flow.
					</p>
				</div>

				<form className="forgot-password-form" onSubmit={handleSubmit}>
					<label className="forgot-password-label" htmlFor="forgot-email">
						Email
					</label>
					<input
						id="forgot-email"
						type="email"
						className="input forgot-password-input"
						placeholder="Enter your email"
						value={email}
						onChange={(event) => setEmail(event.target.value)}
						autoComplete="email"
						required
					/>

					{error && <p className="forgot-password-error">{error}</p>}

					<div className="forgot-password-actions">
						<Button
							className="forgot-password-submit"
							type="submit"
							disabled={isSubmitting}
						>
							{isSubmitting ? "Sending..." : "Send code"}
						</Button>
						<Link className="forgot-password-link" to="/login">
							Back to login
						</Link>
					</div>
				</form>
			</section>
		</main>
	);
}
