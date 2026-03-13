import { NavLink } from "react-router-dom";
import "./Navbar.css";
import logo from "./png/logo/logo.png";


export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="logo-container">
                 <img className="img" src={logo} alt="logo Project O.S.A.L" />
                <label className="project-name">LegacyTrainer</label>
            </div>
            <div className="nav-links">
            <NavLink className="navlink" to="/about">About the company</NavLink>
            <NavLink className="navlink" to="/">Home</NavLink>
            <NavLink className="navlink" to="/possibilites">Possibilites</NavLink>
            <NavLink className="navlink" to="/contact">Contact</NavLink>
            <NavLink className="navlink" to="/support">Support</NavLink>
            <NavLink className="navlink" to="/sing_in">Sing in</NavLink>
            <NavLink className="navlink" to="/test">Test</NavLink>
      
            </div>
        </nav>
    );
}
