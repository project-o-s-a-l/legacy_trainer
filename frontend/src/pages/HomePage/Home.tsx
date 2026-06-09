import { Button } from "@/shared/index.ts";
import { useNavigate } from "react-router-dom";
import { pc } from "@/shared/index";
import { zeroGlith } from "@/shared/index";
import { firstGlith } from "@/shared/index";
import "./Home.css";
import { useAuth } from "@/features/AutchContext/AuthContext";

export default function Home() {
	const { isAuthenticated, loading } = useAuth();

	if (loading) {
		return <div>Loading...</div>;
	}

	const nav = useNavigate();
	return (
		<div>
			<div className="about-site">
				<div className="about-site-content flex-between-start">
					<div className="text-main about-site-text-container box-light">
						<span className="about-site-span">
							<h2 className="about-site-h2">
								A little about the site
							</h2>
						</span>
						<p>
							Upload your code, select the language and difficulty
							level, and get a quick check and recommendations for
							improvement. Learn by doing and improve your
							programming skills with us!
						</p>
					</div>
					<img className="img-pc-main" src={pc} alt="" />
				</div>
			</div>
			<div className="home-cta-section flex-between-center padding-bottom-main">
				<img className="first-bug-main" src={zeroGlith} alt="" />
				<div className="text-main main-page-login-text-container text-center flex-col-center box-light">
					<div className="">
						<p>Ready to test your code?</p>
						<span>
							Check the code. <br /> Get advice.
						</span>
						<span>
							Upload your code, select the language and difficulty
							level, and get instant feedback and recommendations
							for improvement. Learn by doing and improve your
							programming skills with us.
						</span>
					</div>
					<div className="btn-main-page-login-container">
						{isAuthenticated ? (
							<Button onClick={() => nav("/profile")}>
								Profile
							</Button>
						) : (
							<Button onClick={() => nav("/Registration")}>
								Registration
							</Button>
						)}
						{isAuthenticated ? (
							<Button
								onClick={() => nav("/ChooseTask")}
								className="btn-main-page-sign-in"
							>
								Generate Task
							</Button>
						) : (
							<Button
								onClick={() => nav("/login")}
								className="btn-main-page-sign-in"
							>
								Sign In
							</Button>
						)}
					</div>
				</div>
				<img className="second-bug-main" src={firstGlith} alt="" />
			</div>
		</div>
	);
}
