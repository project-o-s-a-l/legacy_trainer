import "./Login.css"

function Login(){
    return (
    <main className="main">
        <form className="login-card">
        <h1>Login</h1>
        <label>
            Email
            <input type="email" placeholder="Enter your email"/>
        </label>

        <label>
            Password
            <input type="password" placeholder="Enter your password"/>
        </label>

        <button type="submit">Login</button>
        <a>Forgot password?</a>

        </form>
    </main>
  )
}

export default Login