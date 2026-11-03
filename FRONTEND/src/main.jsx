import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import LandingPage from "./pages/LandingPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import SettingsPage from "./pages/SettingsPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import VisualsPage from "./pages/VisualsPage";
import "./styles/global.css";
import "./pages/LandingPage.css";
import "./pages/LoginPage.css";
import "./pages/RegisterPage.css";
import "./styles/HomePage.css";

const savedTheme = localStorage.getItem("noteflow_theme");
document.documentElement.dataset.theme = savedTheme === "dark" ? "dark" : "light";

const pages = {
  "/login": LoginPage,
  "/register": RegisterPage,
  "/settings": SettingsPage,
  "/reset-password": ResetPasswordPage,
  "/visuals": VisualsPage,
};
const isAuthenticated = Boolean(localStorage.getItem("noteflow_access_token"));
const Page = window.location.pathname === "/home"
  ? (isAuthenticated ? HomePage : LoginPage)
  : isAuthenticated && window.location.pathname === "/"
    ? HomePage
    : pages[window.location.pathname] ?? LandingPage;

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Page />
  </StrictMode>,
);
