import { useMemo, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./GetEmailCode.css";

type FlowMode = "registration" | "recovery";

type LocationState = {
	email?: string;
	flow?: FlowMode;
};

export default function CodePage() {
	const navigate = useNavigate();
	const location = useLocation();
	const [code, setCode] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [resent, setResent] = useState(false);

	const state = (location.state as LocationState | null) ?? null;
	const flow = state?.flow ?? "registration";

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

	const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();

		if (!/^\d{4,6}$/.test(code.trim())) {
			setError("Enter a valid verification code");
			return;
		}

		setError(null);
		navigate("/login", {
			replace: true,
			state: {
				notice:
					flow === "recovery"
						? "Code accepted in the UI flow. Continue from login."
						: "Registration completed. You can sign in now.",
			},
		});
	};

	return (
		<main className="code-page">
			<section className="code-shell card card-code-gradient">
				<div className="code-copy">
					<p className="code-kicker">{pageCopy.kicker}</p>
					<h1 className="code-title">{pageCopy.title}</h1>
					<p className="code-description">{pageCopy.description}</p>
					{state?.email && (
						<p className="code-email">Code destination: {state.email}</p>
					)}
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
						required
					/>

					{error && <p className="code-error">{error}</p>}

					<div className="code-actions">
						<button type="submit" className="btn-ghost code-button">
							Next
						</button>

						<div className="code-secondary-actions">
							<p className="code-text">Didn't receive the code?</p>
							<button
								type="button"
								className="code-link"
								onClick={() => setResent(true)}
							>
								Resend it
							</button>
							{resent && (
								<span className="code-resent">
									A new code request was prepared in the UI flow.
								</span>
							)}
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
