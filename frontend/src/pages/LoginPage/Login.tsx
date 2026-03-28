import "./Login.css"
import st from "../../shared/assets/images/svg/pngwing.com 1.svg";
 
function Login(){
    return (
    <main className="main">
        <form className="login-card">
        <h1>Login</h1>
        <div className="form-group">
    <label>Email or username</label>
    <input type="email" placeholder="Enter your email" />
  </div>

  <div className="form-group">
    <label>Password</label>
    <input type="password" placeholder="Enter your password" />
  </div>

    <button className="next-btn" type="submit">
    <img src={st} alt="next"/>
    </button>
  <a href="#">Forgot password?</a>
        </form>
    </main>
  )
}

export default Login

