import { NavLink } from "react-router-dom";
import "./Navbar.css";
import logo from '../../shared/assets/logo/logo.png';
import type { AppPage } from "../../shared/types/routes"



type NavbarProps = {
    links: AppPage[];
}

export default function Navbar({ links }: NavbarProps) {
    return (
        <nav className="navbar">
            <div className="logo-container">
                 <img className="logo-img" src={logo} alt="logo Project O.S.A.L" />
                <span className="project-name">LegacyTrainer</span>
            </div>
            <div className="nav-links">
                {links.filter((link) => link.showInNavbar).
                map(link=> (
                    <NavLink key={link.path} className="navlink" to={link.path}>
                        {link.label}
                    </NavLink>
                ))}
            </div>
        </nav>
    );
}
