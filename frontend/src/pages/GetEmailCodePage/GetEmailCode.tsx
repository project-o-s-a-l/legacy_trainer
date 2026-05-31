import { useMemo, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
	confirmPasswordRecoveryCode,
	confirmRegistrationVerificationCode,
	requestPasswordRecoveryCode,
	requestRegistrationVerificationCode,
	type VerificationFlowMode,
} from "@/features/verificationCode/verificationCode";
import "./GetEmailCode.css";

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
		<main className="code-page">
			<section className="code-shell card card-code-gradient">
				<div className="code-copy">
					<p className="code-kicker">{pageCopy.kicker}</p>
					<h1 className="code-title">{pageCopy.title}</h1>
					<p className="code-description">{pageCopy.description}</p>
					<p className="code-email">
						{email
							? `Code destination: ${email}`
							: "Email is unavailable. Restart the flow from the previous screen."}
					</p>
				</div>

				<form className="code-form" onSubmit={handleSubmit}>
					<label className="code-label" htmlFor="verification-code">
						Verification code
					</label>
					<input
						id="verification-code"
						type="text"
						placeholder="Enter code"
						className="input code-input"
						value={code}
						onChange={(event) => setCode(event.target.value)}
						inputMode="numeric"
						autoComplete="one-time-code"
						disabled={!email || isSubmitting}
						required
					/>

					{error && <p className="code-error">{error}</p>}
					{statusMessage && <p className="code-resent">{statusMessage}</p>}

					<div className="code-actions">
						<button
							type="submit"
							className="btn-ghost code-button"
							disabled={!email || isSubmitting}
						>
							{isSubmitting ? "Checking..." : "Next"}
						</button>

						<div className="code-secondary-actions">
							<p className="code-text">Didn't receive the code?</p>
							<button
								type="button"
								className="code-link"
								onClick={() => {
									void handleResend();
								}}
								disabled={!email || isResending}
							>
								{isResending ? "Resending..." : "Resend it"}
							</button>
						</div>
					</div>
				</form>

				<Link
					className="code-back-link"
					to={flow === "recovery" ? "/forgot-password" : "/Registration"}
				>
					Back
				</Link>
			</section>
		</main>
	);
}
