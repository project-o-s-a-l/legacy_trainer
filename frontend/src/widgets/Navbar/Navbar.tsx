import { Link, NavLink } from "react-router-dom";
import "./Navbar.css";
import { logo } from "@/shared/index.ts";
import type { AppPage } from "../../shared/types/routes";

type NavbarProps = {
	links: AppPage[];
	isAuthenticated: boolean;
	onLogout: () => void;
};

export default function Navbar({
	links,
	isAuthenticated,
	onLogout,
}: NavbarProps) {
	return (
		<nav className="navbar">
			<Link className="logo-container" to="/" aria-label="Go to home page">
				<img className="logo-img" src={logo} alt="logo Project O.S.A.L" />
				<span className="project-name">LegacyTrainer</span>
			</Link>

			<div className="nav-links">
				{links
					.filter((link) => link.showInNavbar)
					.map((link) => (
						<div key={link.path} className="nav-item">
							<NavLink
								to={link.path}
								className={({ isActive }) =>
									`navlink ${isActive ? "navlink-active" : ""}`.trim()
								}
							>
								{link.label}
							</NavLink>
						</div>
					))}

				{isAuthenticated && (
					<div className="nav-item">
						<button
							type="button"
							className="navlink navlink-button"
							onClick={onLogout}
						>
							Log out
						</button>
					</div>
				)}
			</div>
		</nav>
	);
}
