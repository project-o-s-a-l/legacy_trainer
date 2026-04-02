
import "./CodePage.css";

export default function CodePage() {
  return (
    <div className="code-page">
      <div className="code-wrapper">
        <div className="code-card">
          <h1 className="code-title">Enter the code</h1>

          <form className="code-form">
            <input
              type="text"
              placeholder="Enter text"
              className="code-input"
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