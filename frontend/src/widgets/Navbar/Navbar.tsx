import { NavLink } from "react-router-dom";
import "./Navbar.css";
import logo from '../../shared/assests/logo/logo.png';
// import { link } from "fs";
import type { AppPage } from "../../shared/types/routes"



type NavbarProps = {
    links: AppPage[];
}

export default function Navbar({ links }: NavbarProps) {
    return (
        <nav className="navbar">
            <div className="logo-container">
                 <img className="img" src={logo} alt="logo Project O.S.A.L" />
                <label className="project-name">LegacyTrainer</label>
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
