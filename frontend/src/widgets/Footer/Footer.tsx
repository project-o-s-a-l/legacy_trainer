import './Footer.css';
import { logo } from '@/shared/index.ts';


export default function Footer() {
    return (
        <footer className='footer'>
            <div className='footer-container'>
            <div className='footer-top-row'>
               <div className="footer-logo-container">
                 <img className="footer-img logo-img" src={logo} alt="logo Project O.S.A.L" />
                <span className="footer-project-name">LegacyTrainer</span>
            </div>
                <span className='footer-info'>The project was created for educational and research purposes</span>
            </div>
                <hr className='footer-divider'/>
                <div className='copyrights'> 
                    <p >All rights reserved &copy; {new Date().getFullYear()} </p>
                    <p className='footer-confidentiality'>Confidentiality</p> 
                </div>
            </div>
        </footer>
    )
}
