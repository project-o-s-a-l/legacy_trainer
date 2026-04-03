import "./Login.css";
import st from "../../shared/assets/images/svg/nextBtn.svg";
import { login_request } from "@/features";
import { useState } from "react";

function Login() {
	const [password, setPassword] = useState("");
	const [identity, setIdentity] = useState("");

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		try {
			await login_request(identity, password);
		} catch (error) {
			console.error(error);
		}
	};
	return (
		<main className="main-login flex-center">
			<form className="card card-auth login-card" onSubmit={handleSubmit}>
				<h1 className="headers-login">Login</h1>
				<div className="form-group-login">
					<label className="label-email-login">Email or username</label>
					<input
						className="input"
						type="email"
						placeholder="Enter your email"
						onChange={(e) => setIdentity(e.target.value)}
					/>
				</div>

				<div className="form-group-login flex-col">
					<label className="label-password-login">Password</label>
					<input
						className="input"
						type="password"
						placeholder="Enter your password"
						onChange={(e) => setPassword(e.target.value)}
					/>
				</div>

				<button className="btn-ghost next-btn-login" type="submit">
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
