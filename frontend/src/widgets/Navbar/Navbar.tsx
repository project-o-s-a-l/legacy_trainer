import { NavLink } from "react-router-dom";
import "./Navbar.css";
import logo from "../../sharder/assests/logo/logo.png";
import { link } from "fs";
import type { AppPage } from "../../shared/types/routres"
import type { NavbarProps } from "../../shared/types/navbarProps";




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
            {/* <NavLink className="navlink" to="/about">About the company</NavLink>
            <NavLink className="navlink" to="/">Home</NavLink>
            <NavLink className="navlink" to="/possibilites">Possibilites</NavLink>
            <NavLink className="navlink" to="/contact">Contact</NavLink>
            <NavLink className="navlink" to="/support">Support</NavLink>
            <NavLink className="navlink" to="/sing_in">Sign in</NavLink>
            <NavLink className="navlink" to="/test">Test</NavLink> */}
      
            </div>
        </nav>
    );
}
