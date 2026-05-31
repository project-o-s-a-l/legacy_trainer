import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Button from "@/shared/ui/Button";
import { completePasswordRecoveryReset } from "@/features/verificationCode/verificationCode";
import "./ResetPassword.css";

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
		<main className="reset-password-page">
			<section className="reset-password-shell card card-code-gradient">
				<div className="reset-password-copy">
					<p className="reset-password-kicker">Password recovery</p>
					<h1 className="reset-password-title">Choose a new password</h1>
					<p className="reset-password-text">
						Set a new password for your account and finish the recovery
						flow.
					</p>
					<p className="reset-password-email">
						{email
							? `Account email: ${email}`
							: "Recovery session is missing. Restart the flow from Forgot password."}
					</p>
				</div>

				<form className="reset-password-form" onSubmit={handleSubmit}>
					<label className="reset-password-label" htmlFor="new-password">
						New password
					</label>
					<input
						id="new-password"
						type="password"
						className="input reset-password-input"
						placeholder="Enter new password"
						value={password}
						onChange={(event) => setPassword(event.target.value)}
						autoComplete="new-password"
						disabled={!email || !resetToken || isSubmitting}
						required
					/>

					<label
						className="reset-password-label"
						htmlFor="confirm-new-password"
					>
						Confirm new password
					</label>
					<input
						id="confirm-new-password"
						type="password"
						className="input reset-password-input"
						placeholder="Confirm new password"
						value={confirmPassword}
						onChange={(event) => setConfirmPassword(event.target.value)}
						autoComplete="new-password"
						disabled={!email || !resetToken || isSubmitting}
						required
					/>

					{error && <p className="reset-password-error">{error}</p>}

					<div className="reset-password-actions">
						<Button
							className="reset-password-submit"
							type="submit"
							disabled={!email || !resetToken || isSubmitting}
						>
							{isSubmitting ? "Saving..." : "Save password"}
						</Button>
						<Link className="reset-password-link" to="/forgot-password">
							Back
						</Link>
					</div>
				</form>
			</section>
		</main>
	);
}
