import { useState } from "react";

import { registerUser } from "../services/api";

function getPasswordStrength(password) {
  if (!password) return null;

  const score = [
    password.length >= 8,
    /[a-z]/.test(password) && /[A-Z]/.test(password),
    /\d/.test(password),
    /[^a-zA-Z\d]/.test(password),
  ].filter(Boolean).length;

  if (score <= 1) return { level: "weak", label: "Weak password" };
  if (score <= 2) return { level: "medium", label: "Medium strength" };
  return { level: "strong", label: "Strong password" };
}

function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const passwordStrength = getPasswordStrength(password);
  const passwordsMatch = confirmPassword.length > 0 && password === confirmPassword;

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setIsSubmitting(true);
    try {
      await registerUser({ fullName, email, password });
      window.location.href = "/login";
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to create your account.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-frame dual-auth-frame signup-page">
      <div className="form-side">
        <div className="signup-grid-bg" aria-hidden="true" />
        <div className="logo">
          <div className="logo-icon">
            <i className="fas fa-layer-group" />
          </div>
          NoteFlow
        </div>

        <header className="auth-header">
          <h1 id="register-title">Create your account</h1>
          <p>Organize your documents and study smarter.</p>
        </header>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full name</label>
            <input id="name" name="name" type="text" placeholder="Jane Doe" value={fullName} onChange={(event) => setFullName(event.target.value)} required />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email address</label>
            <input id="email" name="email" type="email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input id="password" name="password" type="password" placeholder="••••••••" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required />
            {passwordStrength && (
              <div className="password-strength" aria-live="polite">
                <div className={`strength-bar ${passwordStrength.level}`} aria-hidden="true">
                  <span /><span /><span /><span />
                </div>
                <span className={`strength-text ${passwordStrength.level}`}>
                  {passwordStrength.label}
                </span>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirm-password">Confirm password</label>
            <input id="confirm-password" name="confirmPassword" type="password" placeholder="••••••••" minLength={8} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required />
            {confirmPassword && (
              <span className={`password-match${passwordsMatch ? " is-match" : " is-mismatch"}`} aria-live="polite">
                <i className={`fas ${passwordsMatch ? "fa-check-circle" : "fa-times-circle"}`} aria-hidden="true" />
                {passwordsMatch ? "Passwords match" : "Passwords do not match"}
              </span>
            )}
          </div>

          <button type="submit" className="btn-primary-full" disabled={isSubmitting}>
            <i className="fas fa-user-plus" />
            <span>{isSubmitting ? "Creating Account..." : "Create Account"}</span>
          </button>

          {error && <p className="form-error" role="alert">{error}</p>}
          <p className="alt-link">
            Already have an account? <a href="/login">Sign in</a>
          </p>
        </form>

        <div className="signup-features" aria-label="Account benefits">
          <span><i className="fas fa-check" aria-hidden="true" /> Free to start</span>
          <span><i className="fas fa-check" aria-hidden="true" /> No credit card</span>
          <span><i className="fas fa-check" aria-hidden="true" /> Study at your pace</span>
        </div>

        <footer className="signup-footer">
          © 2026 NoteFlow · Built for focused learning
        </footer>
      </div>

      <div className="image-side">
        <a href="/" className="back-link-top">
          <i className="fas fa-arrow-left" /> Back to Home
        </a>
        <img
          src="https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1200&q=80"
          alt="Notes and documents on a desk"
          loading="lazy"
        />
        <div className="signup-image-caption">
          <span>NOTEFLOW</span>
          <p>Your knowledge, organized.</p>
        </div>
      </div>
    </main>
  );
}

export default RegisterPage;
