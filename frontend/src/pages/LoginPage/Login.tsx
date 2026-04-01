import "./Login.css";
import st from "../../shared/assets/images/svg/pngwing.com 1.svg";
import { login_request } from "@/features";
import { useState } from "react";

function Login() {
	const [password, setPassword] = useState("");
	const [email, setEmail] = useState("");

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		try {
			await login_request(email, password);
		} catch (error) {
			console.error(error);
		}
	};
	return (
		<main className="main-login">
			<form className="login-card" onSubmit={handleSubmit}>
				<h1 className="headers-login">Login</h1>
				<div className="form-group-login">
					<label className="label-email-login">Email or username</label>
					<input
						className="input-email-login"
						type="email"
						placeholder="Enter your email"
						onChange={(e) => setEmail(e.target.value)}
					/>
				</div>

				<div className="form-group-login">
					<label className="label-password-login">Password</label>
					<input
						className="input-password-login"
						type="password"
						placeholder="Enter your password"
						onChange={(e) => setPassword(e.target.value)}
					/>
				</div>

				<button className="next-btn-login" type="submit">
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
