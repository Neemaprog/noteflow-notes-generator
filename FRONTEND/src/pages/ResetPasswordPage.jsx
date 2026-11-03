import { useState, useEffect } from "react";
import { resetPassword } from "../services/api";
import "../styles/ResetPasswordPage.css";

function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isValid, setIsValid] = useState(true);

  const token = searchParams.get("token");

  useEffect(() => {
    if (!token) {
      setIsValid(false);
      setError("Invalid or missing reset token. Please request a new password reset.");
    }
  }, [token]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setIsSubmitting(true);
    try {
      await resetPassword({
        token,
        new_password: newPassword,
      });
      
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to reset password.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!isValid) {
    return (
      <main className="auth-frame reset-password-frame">
        <div className="reset-password-container">
          <div className="error-message">
            <i className="fas fa-exclamation-circle" />
            <h2>Invalid Reset Link</h2>
            <p>{error}</p>
            <a href="/login" className="btn-primary-full">
              Back to Login
            </a>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="auth-frame reset-password-frame">
      <div className="reset-password-container">
        <div className="logo">
          <div className="logo-icon">
            <i className="fas fa-layer-group" />
          </div>
          NoteFlow
        </div>

        <header className="auth-header">
          <h1>Set New Password</h1>
          <p>Create a new password for your account.</p>
        </header>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="new-password">New Password</label>
            <input
              id="new-password"
              name="new-password"
              type="password"
              placeholder="••••••••"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              required
              disabled={isSubmitting}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirm-password">Confirm Password</label>
            <input
              id="confirm-password"
              name="confirm-password"
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              disabled={isSubmitting}
              autoComplete="new-password"
            />
          </div>

          <p className="password-hint">
            <i className="fas fa-info-circle" />
            Password must be at least 8 characters long.
          </p>

          <button type="submit" className="btn-primary-full" disabled={isSubmitting || !newPassword || !confirmPassword}>
            <i className="fas fa-lock" />
            <span>{isSubmitting ? "Resetting..." : "Reset Password"}</span>
          </button>

          {error && <p className="form-error" role="alert">{error}</p>}
          
          <p className="back-to-login">
            Remember your password? <a href="/login">Sign in instead</a>
          </p>
        </form>
      </div>
    </main>
  );
}

export default ResetPasswordPage;
