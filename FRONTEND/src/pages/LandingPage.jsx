import { useEffect, useState } from "react";

function LandingPage() {
  const [openPanel, setOpenPanel] = useState(null);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    const handleKeyDown = (event) => {
      if (event.key === "Escape") setOpenPanel(null);
    };

    window.addEventListener("scroll", handleScroll);
    window.addEventListener("keydown", handleKeyDown);
    handleScroll();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <main className="landing-page" id="top">
      <div className="page-inner">
        <nav className={`navbar${isScrolled ? " is-scrolled" : ""}`}>
          <a className="logo" href="#top" aria-label="Back to top">
            <div className="logo-icon">
              <i className="fas fa-layer-group" />
            </div>
            NoteFlow
          </a>
          <div className="nav-links">
            <button type="button" onClick={() => setOpenPanel("features")}>
              Features
            </button>
            <button type="button" onClick={() => setOpenPanel("about")}>
              About
            </button>
            <a href="/login">Login</a>
            <a className="btn-outline" href="/register">
              Sign Up
            </a>
          </div>
        </nav>

        <header className="hero">
          <h1>
            Learn from your documents.
            <span>Organize your knowledge.</span>
          </h1>
          <p>
            Convert documents, recordings and images into clear notes, summaries
            and visual explanations.
          </p>
          <div className="hero-actions">
            <a className="btn-primary" href="/register">
              <i className="fas fa-arrow-right" /> Get Started
            </a>
            <button
              className="btn-secondary"
              type="button"
              onClick={() => setOpenPanel("features")}
            >
              <i className="fas fa-compass" /> Explore Features
            </button>
          </div>

          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-file-alt" />
              </div>
              <h3>Documents</h3>
              <p>Upload and extract text from PDFs, Word files, and images.</p>
              <div className="feature-tag">
                <i className="fas fa-check-circle" /> ready
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-book-open" />
              </div>
              <h3>Study Notes</h3>
              <p>Structured summaries, key points, and editable notes.</p>
              <div className="feature-tag">
                <i className="fas fa-clock" /> auto
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-chart-bar" />
              </div>
              <h3>Visuals</h3>
              <p>User-led diagrams, mind maps, and charts.</p>
              <div className="feature-tag">
                <i className="fas fa-pen" /> interactive
              </div>
            </div>
          </div>
        </header>

        <div className="bottom-bar">
          <div className="check-icon">
            <i className="fas fa-check" />
          </div>
          <span className="bottom-bar-label">Built for focused learning</span>
          <span>·</span>
          <div className="mini-icon indigo">
            <i className="fas fa-folder" />
          </div>
          <div className="mini-icon teal">
            <i className="fas fa-microphone" />
          </div>
          <div className="mini-icon muted">
            <i className="fas fa-clock" />
          </div>
        </div>

        {openPanel && (
          <div
            className="landing-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="panel-title"
            onClick={() => setOpenPanel(null)}
          >
            <div
              className="landing-modal-card"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                className="modal-close"
                type="button"
                aria-label="Close panel"
                onClick={() => setOpenPanel(null)}
              >
                <i className="fas fa-times" />
              </button>
              {openPanel === "features" ? (
                <>
                  <div className="modal-icon">
                    <i className="fas fa-compass" />
                  </div>
                  <h2 id="panel-title">Features</h2>
                  <p>
                    Everything you need to turn your learning materials into
                    clear, useful knowledge.
                  </p>
                  <div className="modal-feature-list">
                    <div>
                      <i className="fas fa-file-alt" />
                      <span>
                        <strong>Documents</strong>Upload and extract text from
                        your files.
                      </span>
                    </div>
                    <div>
                      <i className="fas fa-book-open" />
                      <span>
                        <strong>Study Notes</strong>Create structured summaries
                        and key points.
                      </span>
                    </div>
                    <div>
                      <i className="fas fa-chart-bar" />
                      <span>
                        <strong>Visuals</strong>Build user-led diagrams, mind
                        maps, and charts.
                      </span>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="modal-icon about">
                    <i className="fas fa-layer-group" />
                  </div>
                  <h2 id="panel-title">About NoteFlow</h2>
                  <p>
                    NoteFlow helps you learn from documents, recordings, and
                    images by organizing them into notes and visual
                    explanations.
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

export default LandingPage;
