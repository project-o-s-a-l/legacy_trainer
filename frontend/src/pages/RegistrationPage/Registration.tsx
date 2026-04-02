import "./Registration.css"

function Registration(){

    return (
    <div className="registration-page flex-center">
      <div className="registration-card card card-code-gradient ">
        <h1 className="registration-title">Registration</h1>

        <form className="registration-form flex-col">
          <label className="form-label">
            Username
            <input type="text" placeholder="Enter username" className="input form-input" />
          </label>

          <label className="form-label">
            Email or username
            <input type="text" placeholder="Enter email or username" className="input form-input" />
          </label>
          <label className="form-label">
            Password
            <input type="password" placeholder="Enter password" className="input form-input" />
          </label>

          <label className="form-label">
            Confirm your password
            <input type="password" placeholder="Enter your password" className="input form-input" />
          </label>

          <button type="submit" className="btn-ghost btn-submit-registration">
            Get code
          </button>
        </form>
      </div>
    </div>
  );
}
export default Registration