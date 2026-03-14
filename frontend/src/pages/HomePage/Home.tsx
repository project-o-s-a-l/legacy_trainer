import Footer from "../../widgets/Footer/Footer";
import zeroImg from "../../shared/assests/images/00-image.png";
import oneImg from "../../shared/assests/images/01-image.png";
import twoImg from "../../shared/assests/images/02-image.png";

export default function Home() {
  return (
    <div>
      <div className="about-site">
        <div className="about-site-content">
          <div className="about-site-text">
            <span>
              A little about <br /> the site
            </span>
            <p>
              Upload your code, select the language and difficulty level, and
              get a quick check and recommendations for improvement. Learn by
              doing and improve your programming skills with us!
            </p>
          </div>
          <img className="img-pc-main" src={zeroImg} alt="" />
        </div>
      </div>
      <div className="main-page-login-container">
        <img className="first-bug-main" src={oneImg} alt="" />
        <div className="main-page-login-text-container">
          <p>Ready to test your code?</p>
          <text>
            Check the code. <br /> Get advice.
          </text>{" "}
          <br />
          <span>
            Upload your code, select the language and difficulty level, and get
            instant feedback and recommendations for improvement. Learn by doing
            and improve your programming skills with us.
          </span>
          <div className="btn-main-page-login-container">
            <button className="btn-main-page-sign-up">Registration</button>{" "}
            <br />
            <button className="btn-main-page-sign-in">Sign in</button>
          </div>
        </div>
        <img className="second-bug-main" src={twoImg} alt="" />
      </div>
      <Footer></Footer>
    </div>
  );
}
