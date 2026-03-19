import './Footer.css';
import logo from '../../shared/assets/logo/logo.png';


export default function Footer() {
    return (
        <footer className='footer'>
            <div className='footer-container'>
            <div className='footer-top-row'>
               <div className="footer-logo-container">
                 <img className="footer-img" src={logo} alt="logo Project O.S.A.L" />
                <label className="footer-project-name">LegacyTrainer</label>
            </div>
                <label className='footer-info'>The project was created for educational and research purposes</label>
            </div>
                <hr style={{border: "1px solid white", width: "99.9%" }}/>
                <div className='copyrights'> 
                    <p >All rights reserved &copy; {new Date().getFullYear()} </p>
                    <p style={{paddingLeft: "25px"}}>Confidentiality</p> 
                </div>
            </div>
        </footer>
    )
}
