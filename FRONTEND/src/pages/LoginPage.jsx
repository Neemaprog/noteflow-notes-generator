import { useState } from "react";

import { loginUser } from "../services/api";
import ForgotPasswordModal from "../components/ForgotPasswordModal";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [forgotOpen, setForgotOpen] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const result = await loginUser({ email, password });
      localStorage.setItem("noteflow_access_token", result.access_token);
      window.location.href = "/home";
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to login.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-frame dual-auth-frame login-page">
      <div className="form-side">
        <div className="login-grid-bg" aria-hidden="true" />
        <div className="logo">
          <div className="logo-icon">
            <i className="fas fa-layer-group" />
          </div>
          NoteFlow
        </div>

        <header className="auth-header">
          <h1 id="login-title">Welcome back</h1>
          <p>Continue your learning workspace.</p>
        </header>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email address</label>
            <input id="email" name="email" type="email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input id="password" name="password" type="password" placeholder="••••••••" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </div>

          <div className="forgot-row">
            <button type="button" className="forgot-link" onClick={() => setForgotOpen(true)}>Forgot password?</button>
          </div>

          <button type="submit" className="btn-primary-full" disabled={isSubmitting}>
            <i className="fas fa-arrow-right-to-bracket" />
            <span>{isSubmitting ? "Signing In..." : "Sign In"}</span>
          </button>

          {error && <p className="form-error" role="alert">{error}</p>}
          <p className="alt-link">
            Don't have an account? <a href="/register">Create one</a>
          </p>
        </form>
      </div>

      <div className="image-side">
        <a href="/" className="back-link-top">
          <i className="fas fa-arrow-left" /> Back to Home
        </a>
        <img
          src="https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=1200&q=80"
          alt="Study notes and writing on a desk"
          loading="lazy"
        />
        <div className="login-image-caption">
          <span>NOTEFLOW</span>
          <p>Turn your documents into knowledge.</p>
        </div>
      </div>

      <ForgotPasswordModal isOpen={forgotOpen} onClose={() => setForgotOpen(false)} />
    </main>
  );
}

export default LoginPage;
