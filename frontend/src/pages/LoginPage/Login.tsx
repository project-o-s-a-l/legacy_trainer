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
		<main className="main">
			<form className="login-card" onSubmit={handleSubmit}>
				<h1 className="H1_login">Login</h1>
				<div className="form-group">
					<label className="email_l">Email or username</label>
					<input
						type="email"
						placeholder="Enter your email"
						onChange={(e) => setEmail(e.target.value)}
					/>
				</div>

				<div className="form-group">
					<label className="password_l">Password</label>
					<input
						type="password"
						placeholder="Enter your password"
						onChange={(e) => setPassword(e.target.value)}
					/>
				</div>

				<button className="next-btn" type="submit">
					<img src={st} alt="next" />
				</button>
				<a className="ar1" href="#">
					Forgot password?
				</a>
			</form>
		</main>
	);
}
export default Login;
