import { useEffect, useState } from "react";

import { getCurrentUser, updateCurrentUser } from "../services/api";
import "../styles/HomePage.css";
import "../styles/SettingsPage.css";

function SettingsPage() {
  const [theme, setTheme] = useState(
    document.documentElement.dataset.theme === "dark" ? "dark" : "light",
  );
  const [user, setUser] = useState(null);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    getCurrentUser()
      .then((currentUser) => {
        setUser(currentUser);
        setFullName(currentUser.full_name);
        setEmail(currentUser.email);
      })
      .catch(() => {
        localStorage.removeItem("noteflow_access_token");
        window.location.href = "/login";
      });
  }, []);

  const handleSaveProfile = async (event) => {
    event.preventDefault();
    setMessage("");
    setIsSaving(true);
    try {
      const updatedUser = await updateCurrentUser({ fullName, email });
      setUser(updatedUser);
      setFullName(updatedUser.full_name);
      setEmail(updatedUser.email);
      setMessage("Profile updated successfully.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to update profile.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleThemeChange = (nextTheme) => {
    setTheme(nextTheme);
    localStorage.setItem("noteflow_theme", nextTheme);
    document.documentElement.dataset.theme = nextTheme;
  };

  const handleLogout = () => {
    localStorage.removeItem("noteflow_access_token");
    window.location.href = "/";
  };

  return (
    <div className="app-frame settings-frame">
      <div className="topbar">
        <div className="topbar-left">
          <a className="logo" href="/home">
            <div className="logo-icon"><i className="fas fa-layer-group" /></div>
            NoteFlow
          </a>
        </div>
        <div className="user-info">
          <div className="user-avatar">{user?.full_name?.slice(0, 1).toUpperCase() ?? "..."}</div>
          <div className="user-name">{user?.full_name ?? "Loading..."}</div>
        </div>
      </div>

      <div className="main-layout">
        <aside className="sidebar">
          <a className="sidebar-item" href="/home"><i className="fas fa-plus" /> New</a>
          <a className="sidebar-item" href="/home"><i className="fas fa-clock-rotate-left" /> History</a>
          <a className="sidebar-item" href="/visuals"><i className="fas fa-chart-bar" /> Visuals</a>
          <a className="sidebar-item active" href="/settings"><i className="fas fa-cog" /> Settings</a>
          <div className="sidebar-divider" />
          <button className="sidebar-item logout" type="button" onClick={handleLogout}>
            <i className="fas fa-arrow-right-from-bracket" /> Logout
          </button>
        </aside>

        <main className="main-content settings-content">
          <div className="settings-title">
            <span>PERSONALIZE</span>
            <h1>Settings</h1>
            <p>Manage your account and choose how NoteFlow looks.</p>
          </div>

          <section className="settings-card appearance-card" aria-labelledby="appearance-title">
            <h2 id="appearance-title">Appearance</h2>
            <p className="settings-card-description">Choose the theme that feels best for you.</p>
            <div className="theme-options" role="group" aria-label="Color theme">
              <button
                className={`theme-option${theme === "light" ? " selected" : ""}`}
                type="button"
                aria-pressed={theme === "light"}
                onClick={() => handleThemeChange("light")}
              >
                <i className="fas fa-sun" aria-hidden="true" />
                <span>Light mode</span>
              </button>
              <button
                className={`theme-option${theme === "dark" ? " selected" : ""}`}
                type="button"
                aria-pressed={theme === "dark"}
                onClick={() => handleThemeChange("dark")}
              >
                <i className="fas fa-moon" aria-hidden="true" />
                <span>Dark mode</span>
              </button>
            </div>
          </section>

          <form className="settings-card" onSubmit={handleSaveProfile}>
            <h2>Profile</h2>
            <p className="settings-card-description">Keep your name and email address up to date.</p>

            <label htmlFor="settings-name">Full name</label>
            <input id="settings-name" type="text" value={fullName} onChange={(event) => setFullName(event.target.value)} required minLength={1} maxLength={150} />

            <label htmlFor="settings-email">Email address</label>
            <input id="settings-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />

            <div className="settings-actions">
              {message && <span className="settings-message">{message}</span>}
              <button className="btn-generate" type="submit" disabled={isSaving}>
                {isSaving ? "Saving..." : "Save profile"}
              </button>
            </div>
          </form>
        </main>
      </div>
    </div>
  );
}

export default SettingsPage;
