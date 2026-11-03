import { useState } from "react";
import { forgotPassword } from "../services/api";
import "../styles/ForgotPasswordModal.css";

function ForgotPasswordModal({ isOpen, onClose }) {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    setIsSubmitting(true);

    try {
      await forgotPassword({ email });
      setMessage("Check your email for a password reset link. It expires in 1 hour.");
      setEmail("");
      setTimeout(() => {
        onClose();
        setMessage("");
      }, 3000);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to process request.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="forgot-password-overlay" onClick={onClose}>
      <div className="forgot-password-modal" onClick={(e) => e.stopPropagation()}>
        <div className="forgot-password-header">
          <h2>Reset Your Password</h2>
          <button
            className="forgot-password-close"
            onClick={onClose}
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <form className="forgot-password-form" onSubmit={handleSubmit}>
          <p className="forgot-password-description">
            Enter the email address associated with your NoteFlow account, and we'll send you a link to reset your password.
          </p>

          <div className="form-group">
            <label htmlFor="reset-email">Email address</label>
            <input
              id="reset-email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isSubmitting}
              autoComplete="email"
            />
          </div>

          {error && <p className="form-error" role="alert">{error}</p>}
          {message && <p className="form-success" role="alert">{message}</p>}

          <button
            type="submit"
            className="btn-primary-full"
            disabled={isSubmitting || !email}
          >
            {isSubmitting ? "Sending..." : "Send Reset Link"}
          </button>

          <p className="forgot-password-note">
            Didn't receive an email? Check your spam folder or try again.
          </p>
        </form>
      </div>
    </div>
  );
}

export default ForgotPasswordModal;
