
import "./GetEmailCode.css";

export default function CodePage() {
  return (
    <div className="code-page flex-center">
      <div className="code-wrapper">
        <div className="code-card card card-code-gradient">
          <h1 className="code-title">Enter the code</h1>

          <form className="code-form">
            <input
              type="text"
              placeholder="Enter text"
              className="input input-compact"
            />

            <button type="submit" className="code-button">
              Next
            </button>
          </form>

          <p className="code-text">Didn't receive the code?</p>
          <a href="#" className="code-link">
            Resend it?
          </a>
        </div>

        <div className="image-placeholder">
          {/* Здесь позже будет картинка */}
        </div>
      </div>
    </div>
  );
}