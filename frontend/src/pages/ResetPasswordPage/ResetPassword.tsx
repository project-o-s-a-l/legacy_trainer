import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { completePasswordRecoveryReset } from "@/features/verificationCode/verificationCode";
import "../AuthProfileTheme.css";

type ResetPasswordLocationState = {
	email?: string;
	resetToken?: string;
};

export default function ResetPassword() {
	const navigate = useNavigate();
	const location = useLocation();
	const state = (location.state as ResetPasswordLocationState | null) ?? null;
	const email = state?.email?.trim() ?? "";
	const resetToken = state?.resetToken?.trim() ?? "";

	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		if (!email || !resetToken) {
			setError("Restart the password recovery flow to continue.");
			return;
		}

		try {
			setError(null);
			setIsSubmitting(true);
			const response = await completePasswordRecoveryReset(
				email,
				password,
				confirmPassword,
				resetToken,
			);

			navigate("/login", {
				replace: true,
				state: {
					notice:
						response.message || "Password updated. You can sign in now.",
				},
			});
		} catch (error) {
			setError(
				error instanceof Error
					? error.message
					: "Unable to update password",
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
						<p className="auth-profile-panel-kicker">New credentials</p>
						<h2 className="auth-profile-panel-title">Reset password</h2>
					</div>

					<form className="auth-profile-form" onSubmit={handleSubmit}>
						<label className="auth-profile-field" htmlFor="new-password">
							<span className="auth-profile-label">New password</span>
							<input
								id="new-password"
								type="password"
								className="input auth-profile-input"
								placeholder="Enter new password"
								value={password}
								onChange={(event) => setPassword(event.target.value)}
								autoComplete="new-password"
								disabled={!email || !resetToken || isSubmitting}
								required
							/>
						</label>

						<label
							className="auth-profile-field"
							htmlFor="confirm-new-password"
						>
							<span className="auth-profile-label">Confirm new password</span>
							<input
								id="confirm-new-password"
								type="password"
								className="input auth-profile-input"
								placeholder="Confirm new password"
								value={confirmPassword}
								onChange={(event) => setConfirmPassword(event.target.value)}
								autoComplete="new-password"
								disabled={!email || !resetToken || isSubmitting}
								required
							/>
						</label>

						{error && (
							<p className="auth-profile-message auth-profile-message--error">
								{error}
							</p>
						)}

						<div className="auth-profile-actions">
							<Link className="auth-profile-link" to="/forgot-password">
								Back
							</Link>
							<button
								className="auth-profile-submit"
								type="submit"
								disabled={!email || !resetToken || isSubmitting}
							>
								{isSubmitting ? "Saving..." : "Save password"}
							</button>
						</div>
					</form>
				</section>
			</section>
		</main>
	);
}
