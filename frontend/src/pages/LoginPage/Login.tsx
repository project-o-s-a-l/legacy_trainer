import "./Login.css";
import st from "../../shared/assets/images/svg/pngwing.com 1.svg";
import { login_request } from "@/features";
import { useState } from "react";

function Login() {
	const [password, setPassword] = useState("");
	const [email, setEmail] = useState("");
	return (
		<main className="main">
			<form className="login-card">
				<h1>Login</h1>
				<div className="form-group">
					<label>Email or username</label>
					<input
						type="email"
						placeholder="Enter your email"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
					/>
				</div>

				<div className="form-group">
					<label>Password</label>
					<input
						type="password"
						placeholder="Enter your password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
					/>
				</div>

				<button
					className="next-btn"
					type="submit"
					onClick={async () => {
						try {
							login_request(email, password);
						} catch (error) {
							console.error(error);
						}
					}}
				>
					<img src={st} alt="next" />
				</button>
				<a href="#">Forgot password?</a>
			</form>
		</main>
	);
}

export default Login;
