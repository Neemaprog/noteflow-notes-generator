import { useEffect, useState } from "react";

import {
  generateVisual,
  getCurrentUser,
  getVisualFile,
  listNotes,
  listVisuals,
} from "../services/api";
import "../styles/HomePage.css";
import "../styles/VisualsPage.css";

function VisualPreview({ visual, onOpen }) {
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let objectUrl;

    getVisualFile(visual.id, { signal: controller.signal })
      .then((file) => {
        objectUrl = URL.createObjectURL(file);
        setImageUrl(objectUrl);
      })
      .catch((loadError) => {
        if (!controller.signal.aborted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Unable to load visual preview.",
          );
        }
      });

    return () => {
      controller.abort();
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [visual.id]);

  if (error) return <p className="visual-preview-message">{error}</p>;
  if (!imageUrl) return <p className="visual-preview-message">Loading visual...</p>;

  return (
    <button
      className="visual-preview-button"
      type="button"
      onClick={() => onOpen({ id: visual.id, name: visual.visual_name, imageUrl })}
      aria-label={`Open ${visual.visual_name} in full-size view`}
    >
      <img src={imageUrl} alt={visual.visual_name} />
      <span>Click to enlarge</span>
    </button>
  );
}

function VisualsPage() {
  const [user, setUser] = useState(null);
  const [notes, setNotes] = useState([]);
  const [selectedNoteId, setSelectedNoteId] = useState("");
  const [visuals, setVisuals] = useState([]);
  const [visualType, setVisualType] = useState("diagram");
  const [colorScheme, setColorScheme] = useState("colorful");
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeVisual, setActiveVisual] = useState(null);
  const [message, setMessage] = useState(
    "Select a note to create a visual explanation.",
  );

  useEffect(() => {
    Promise.all([getCurrentUser(), listNotes()])
      .then(([currentUser, noteList]) => {
        setUser(currentUser);
        setNotes(noteList);
        if (noteList.length > 0) setSelectedNoteId(noteList[0].id);
      })
      .catch(() => {
        localStorage.removeItem("noteflow_access_token");
        window.location.href = "/login";
      });
  }, []);

  useEffect(() => {
    if (!selectedNoteId) {
      setVisuals([]);
      return;
    }
    listVisuals(selectedNoteId)
      .then(setVisuals)
      .catch(() => setVisuals([]));
  }, [selectedNoteId]);

  useEffect(() => {
    if (!activeVisual) return undefined;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") setActiveVisual(null);
    };
    document.addEventListener("keydown", handleKeyDown);
    document.body.classList.add("visual-lightbox-open");
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.classList.remove("visual-lightbox-open");
    };
  }, [activeVisual]);

  const selectedNote = notes.find((note) => note.id === selectedNoteId);

  const handleGenerate = async (event) => {
    event.preventDefault();
    if (!selectedNoteId || !prompt.trim()) {
      setMessage("Select a note and describe the visual you want.");
      return;
    }

    setIsGenerating(true);
    setMessage("Generating your visual...");
    try {
      const visual = await generateVisual(selectedNoteId, {
        visual_type: visualType,
        prompt: prompt.trim(),
        color_scheme: colorScheme,
        file_format: "svg",
      });
      setVisuals((current) => [visual, ...current]);
      setPrompt("");
      setMessage("Visual generated successfully.");
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Unable to generate visual.",
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("noteflow_access_token");
    window.location.href = "/";
  };

  return (
    <div className="app-frame visuals-frame">
      <div className="topbar">
        <div className="topbar-left">
          <a className="logo" href="/home">
            <div className="logo-icon">
              <i className="fas fa-layer-group" />
            </div>
            NoteFlow
          </a>
        </div>
        <div className="user-info">
          <div className="user-avatar">
            {user?.full_name?.slice(0, 1).toUpperCase() ?? "..."}
          </div>
          <div className="user-name">{user?.full_name ?? "Loading..."}</div>
        </div>
      </div>

      <div className="main-layout">
        <aside className="sidebar">
          <a className="sidebar-item" href="/home">
            <i className="fas fa-plus" /> New
          </a>
          <a className="sidebar-item" href="/home">
            <i className="fas fa-clock-rotate-left" /> History
          </a>
          <a className="sidebar-item active" href="/visuals">
            <i className="fas fa-chart-bar" /> Visuals
          </a>
          <a className="sidebar-item" href="/settings">
            <i className="fas fa-cog" /> Settings
          </a>
          <div className="sidebar-divider" />
          <button
            className="sidebar-item logout"
            type="button"
            onClick={handleLogout}
          >
            <i className="fas fa-arrow-right-from-bracket" /> Logout
          </button>
        </aside>

        <main className="main-content visuals-content">

          <form className="visual-generator-card" onSubmit={handleGenerate}>
            <div className="visual-form-header">
              <p>Choose a note you want to visualize.</p>
            </div>

            <label htmlFor="visual-note">Select a note</label>
            <select
              id="visual-note"
              value={selectedNoteId}
              onChange={(event) => setSelectedNoteId(event.target.value)}
              disabled={notes.length === 0}
            >
              {notes.length === 0 && (
                <option value="">No notes available</option>
              )}
              {notes.map((note) => (
                <option key={note.id} value={note.id}>
                  {note.title}
                </option>
              ))}
            </select>

            <div className="visual-form-grid">
              <div>
                <label htmlFor="visual-type">Visual type</label>
                <select
                  id="visual-type"
                  value={visualType}
                  onChange={(event) => setVisualType(event.target.value)}
                >
                  <option value="diagram">Diagram</option>
                  <option value="graph">Graph</option>
                  <option value="chart">Chart</option>
                  <option value="infographic">Infographic</option>
                </select>
              </div>
              <div>
                <label htmlFor="color-scheme">Color scheme</label>
                <select
                  id="color-scheme"
                  value={colorScheme}
                  onChange={(event) => setColorScheme(event.target.value)}
                >
                  <option value="colorful">Colorful</option>
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>
            </div>

            <label htmlFor="visual-prompt">Describe the visual you want</label>
            <textarea
              id="visual-prompt"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Show the main concepts and how they relate to one another..."
              rows="4"
            />
            <div className="visual-submit-row">
              <span>
                {selectedNote
                  ? `Based on: ${selectedNote.title}`
                  : "No note selected"}
              </span>
              <button
                className="btn-generate"
                type="submit"
                disabled={isGenerating || !selectedNoteId}
              >
                {isGenerating ? "Generating..." : "Generate Visual"}
              </button>
            </div>
          </form>

          <div className="status-panel visual-status">{message}</div>

          <section className="visual-results">
            <div className="section-heading">
              <h2>Generated visuals</h2>
              <span>{visuals.length} saved</span>
            </div>
            {visuals.length === 0 ? (
              <div className="visual-empty">
                <i className="fas fa-chart-pie" />
                <h3>Your visuals will appear here</h3>
                <p>Generate a diagram from one of your study notes.</p>
              </div>
            ) : (
              <div className="visual-grid">
                {visuals.map((visual) => (
                  <article className="visual-card" key={visual.id}>
                    <div className="visual-preview">
                      <VisualPreview visual={visual} onOpen={setActiveVisual} />
                    </div>
                    <div className="visual-card-body">
                      <span className="visual-type-pill">
                        {visual.visual_type}
                      </span>
                      <h3>{visual.visual_name}</h3>
                      <p>{visual.description || visual.generation_prompt}</p>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
          {activeVisual && (
            <div
              className="visual-lightbox"
              role="dialog"
              aria-modal="true"
              aria-label={activeVisual.name}
              onClick={() => setActiveVisual(null)}
            >
              <button
                className="visual-lightbox-close"
                type="button"
                aria-label="Close enlarged visual"
                onClick={() => setActiveVisual(null)}
              >
                &times;
              </button>
              <img
                src={activeVisual.imageUrl}
                alt={activeVisual.name}
                onClick={(event) => event.stopPropagation()}
              />
              <p>{activeVisual.name} · Press Esc or click outside to close</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default VisualsPage;
