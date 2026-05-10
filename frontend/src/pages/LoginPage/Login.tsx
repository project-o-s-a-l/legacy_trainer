import "./Login.css";
import st from "../../shared/assets/images/svg/nextBtn.svg";
import { login_request } from "@/features";
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/AuthContext";

function Login() {
	const navigate = useNavigate();
	const { refreshAuth } = useAuth();

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
		<main className="main-login flex-center">
			<form className="card card-auth login-card" onSubmit={handleSubmit}>
				<h1 className="headers-login">Login</h1>

				<div className="form-group-login">
					<label className="label-email-login" htmlFor="identity">
						Email or username
					</label>

					<input
						id="identity"
						className="input"
						type="text"
						placeholder="Enter your email or username"
						value={identity}
						onChange={(e) => setIdentity(e.target.value)}
						autoComplete="username"
						required
					/>
				</div>

				<div className="form-group-login flex-col">
					<label className="label-password-login" htmlFor="password">
						Password
					</label>

					<input
						id="password"
						className="input"
						type="password"
						placeholder="Enter your password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						autoComplete="current-password"
						required
					/>
				</div>

				{error && <p className="login-error">{error}</p>}

				<button
					className="btn-ghost next-btn-login"
					type="submit"
					disabled={isSubmitting}
				>
					<img src={st} alt="next" />
				</button>

				<a className="forgot-password-login" href="#">
					Forgot password?
				</a>
			</form>
		</main>
	);
}

export default Login;