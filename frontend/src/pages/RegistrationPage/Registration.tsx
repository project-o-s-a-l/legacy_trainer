import "./Registration.css"

function Registration(){

    return (
    <div className="registration-page">
      <div className="registration-card">
        <h1 className="registration-title">Registration</h1>

        <form className="registration-form">
          <label className="form-label">
            Username
            <input type="text" placeholder="Enter username" className="form-input" />
          </label>

          <label className="form-label">
            Email or username
            <input type="text" placeholder="Enter email or username" className="form-input" />
          </label>
          <label className="form-label">
            Password
            <input type="password" placeholder="Enter password" className="form-input" />
          </label>

          <label className="form-label">
            Confirm your password
            <input type="password" placeholder="Enter your password" className="form-input" />
          </label>

          <button type="submit" className="btn-submit-registration">
            Get code
          </button>
        </form>
      </div>
    </div>
  );
}
export default Registration