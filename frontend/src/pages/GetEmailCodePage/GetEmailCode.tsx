import { useMemo, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
	confirmPasswordRecoveryCode,
	confirmRegistrationVerificationCode,
	requestPasswordRecoveryCode,
	requestRegistrationVerificationCode,
	type VerificationFlowMode,
} from "@/features/verificationCode/verificationCode";
import "../AuthProfileTheme.css";

type LocationState = {
	email?: string;
	flow?: VerificationFlowMode;
};

export default function CodePage() {
	const navigate = useNavigate();
	const location = useLocation();
	const [code, setCode] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [statusMessage, setStatusMessage] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [isResending, setIsResending] = useState(false);

	const state = (location.state as LocationState | null) ?? null;
	const flow = state?.flow ?? "registration";
	const email = state?.email?.trim() ?? "";

	const pageCopy = useMemo(
		() =>
			flow === "recovery"
				? {
						kicker: "Password recovery",
						title: "Check your email",
						description:
							"Enter the verification code to continue recovering access to your account.",
				  }
				: {
						kicker: "Registration",
						title: "Confirm your email",
						description:
							"Enter the verification code to continue the account setup flow.",
				  },
		[flow],
	);

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		if (!email) {
			setError("Open this page from the previous step to continue.");
			return;
		}

		try {
			setError(null);
			setStatusMessage(null);
			setIsSubmitting(true);

			if (flow === "recovery") {
				const response = await confirmPasswordRecoveryCode(email, code);
				navigate("/reset-password", {
					replace: true,
					state: {
						email,
						resetToken: response.resetToken,
					},
				});
				return;
			}

			const response = await confirmRegistrationVerificationCode(email, code);
			navigate("/login", {
				replace: true,
				state: {
					notice: response.message || "Registration completed. You can sign in now.",
				},
			});
		} catch (error) {
			setError(
				error instanceof Error
					? error.message
					: "Unable to verify the code",
			);
		} finally {
			setIsSubmitting(false);
		}
	};

	const handleResend = async () => {
		if (!email) {
			setError("Open this page from the previous step to continue.");
			return;
		}

		try {
			setError(null);
			setStatusMessage(null);
			setIsResending(true);

			const response =
				flow === "recovery"
					? await requestPasswordRecoveryCode(email)
					: await requestRegistrationVerificationCode(email);

			setStatusMessage(
				response.message || "A new verification code request was sent.",
			);
		} catch (error) {
			setError(
				error instanceof Error
					? error.message
					: "Unable to resend the code",
			);
		} finally {
			setIsResending(false);
		}
	};

	return (
		<main className="auth-profile-page">
			<section className="auth-profile-shell auth-profile-shell--single">
				<section className="auth-profile-card auth-profile-form-panel auth-profile-form-panel--single">
					<div className="auth-profile-form-header">
						<p className="auth-profile-panel-kicker">{pageCopy.kicker}</p>
						<h2 className="auth-profile-panel-title">{pageCopy.title}</h2>
						<p className="auth-profile-message">{pageCopy.description}</p>
						<p className="auth-profile-message">
							{email
								? `Code destination: ${email}`
								: "Email is unavailable. Restart the flow from the previous screen."}
						</p>
					</div>

					<form className="auth-profile-form" onSubmit={handleSubmit}>
						<label className="auth-profile-field" htmlFor="verification-code">
							<span className="auth-profile-label">Verification code</span>
							<input
								id="verification-code"
								type="text"
								placeholder="Enter code"
								className="input auth-profile-input"
								value={code}
								onChange={(event) => setCode(event.target.value)}
								inputMode="numeric"
								autoComplete="one-time-code"
								disabled={!email || isSubmitting}
								required
							/>
						</label>

						{error && (
							<p className="auth-profile-message auth-profile-message--error">
								{error}
							</p>
						)}
						{statusMessage && (
							<p className="auth-profile-message auth-profile-message--success">
								{statusMessage}
							</p>
						)}

						<div className="auth-profile-helper-panel">
							<p className="auth-profile-helper-title">
								Didn't receive the code?
							</p>
							<p className="auth-profile-helper-text">
								Request a new one and continue from the same step.
							</p>
							<button
								type="button"
								className="auth-profile-link-button"
								onClick={() => {
									void handleResend();
								}}
								disabled={!email || isResending}
							>
								{isResending ? "Resending..." : "Resend it"}
							</button>
						</div>

						<div className="auth-profile-actions">
							<Link
								className="auth-profile-link"
								to={flow === "recovery" ? "/forgot-password" : "/Registration"}
							>
								Back
							</Link>
							<button
								type="submit"
								className="auth-profile-submit"
								disabled={!email || isSubmitting}
							>
								{isSubmitting ? "Checking..." : "Next"}
							</button>
						</div>
					</form>
				</section>
			</section>
		</main>
	);
}
