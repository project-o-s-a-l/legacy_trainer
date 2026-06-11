import "../AuthProfileTheme.css";
import st from "../../shared/assets/images/svg/nextBtn.svg";
import { login_request } from "@/features";
import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/useAuth";

type LoginLocationState = {
	notice?: string;
};

function Login() {
	const navigate = useNavigate();
	const location = useLocation();
	const { refreshAuth } = useAuth();
	const notice = (location.state as LoginLocationState | null)?.notice;

	const [password, setPassword] = useState("");
	const [identity, setIdentity] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [isSubmitting, setIsSubmitting] = useState(false);

	const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
		e.preventDefault();

		try {
			setError(null);
			setIsSubmitting(true);

			await login_request(identity, password);
			await refreshAuth();

			navigate("/", { replace: true });
		} catch (error) {
			console.error(error);
			setError("Invalid login or password");
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<main className="auth-profile-page">
			<section className="auth-profile-shell auth-profile-shell--single">
				<section className="auth-profile-card auth-profile-form-panel auth-profile-form-panel--single">
					<div className="auth-profile-form-header">
						<p className="auth-profile-panel-kicker">Credentials</p>
						<h2 className="auth-profile-panel-title">Login</h2>
					</div>

					<form className="auth-profile-form" onSubmit={handleSubmit}>
						<label className="auth-profile-field" htmlFor="identity">
							<span className="auth-profile-label">Email or username</span>
							<input
								id="identity"
								className="input auth-profile-input"
								type="text"
								placeholder="Enter your email or username"
								value={identity}
								onChange={(e) => setIdentity(e.target.value)}
								autoComplete="username"
								required
							/>
						</label>

						<label className="auth-profile-field" htmlFor="password">
							<span className="auth-profile-label">Password</span>
							<input
								id="password"
								className="input auth-profile-input"
								type="password"
								placeholder="Enter your password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								autoComplete="current-password"
								required
							/>
						</label>

						{error && (
							<p className="auth-profile-message auth-profile-message--error">
								{error}
							</p>
						)}
						{notice && (
							<p className="auth-profile-message auth-profile-message--success">
								{notice}
							</p>
						)}

						<div className="auth-profile-actions">
							<Link className="auth-profile-link" to="/forgot-password">
								Forgot password?
							</Link>
							<button
								className="btn-ghost auth-profile-arrow-button"
								type="submit"
								disabled={isSubmitting}
							>
								<img src={st} alt="next" />
							</button>
						</div>
					</form>
				</section>
			</section>
		</main>
	);
}

export default Login;
