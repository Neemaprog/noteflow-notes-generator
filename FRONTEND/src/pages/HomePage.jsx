import { useEffect, useRef, useState } from "react";

import {
  createConversation,
  generateNotesForDocument,
  getConversation,
  getCurrentUser,
  exportNote,
  getDocument,
  getNote,
  listConversations,
  sendConversationMessage,
  uploadDocument,
} from "../services/api";

async function waitForDocumentReady(documentId, maxAttempts = 30) {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const document = await getDocument(documentId);
    if (document.processing_status === "completed") {
      return document;
    }
    if (document.processing_status === "failed") {
      throw new Error(
        "The uploaded file could not be processed. Please try another file.",
      );
    }
    await new Promise((resolve) => setTimeout(resolve, 1500));
  }

  throw new Error(
    "The file is still processing. Please wait a moment and try again.",
  );
}

function cleanNoteContent(content) {
  return content
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/__(.*?)__/g, "$1")
    .replace(/^\s*[-*]\s+/gm, "• ")
    .replace(/^\s*>\s?/gm, "")
    .trim();
}

function HomePage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [instructions, setInstructions] = useState("");
  const [generatedNote, setGeneratedNote] = useState(null);
  const [historyDocument, setHistoryDocument] = useState(null);
  const [statusMessage, setStatusMessage] = useState("No file selected yet.");
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationMessage, setConversationMessage] = useState("");
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const [outputFormat, setOutputFormat] = useState("pdf");
  const [isExporting, setIsExporting] = useState(false);

  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const activeStreamRef = useRef(null);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("noteflow_access_token");
        window.location.href = "/login";
      });

    listConversations()
      .then(setConversations)
      .catch(() => setConversations([]));
  }, []);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === "Escape") setIsSidebarOpen(false);
    };

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, []);

  const handleOpenHistory = async () => {
    setIsHistoryOpen((open) => !open);
    if (!isHistoryOpen) {
      try {
        setConversations(await listConversations());
      } catch {
        setStatusMessage("Unable to load conversation history.");
      }
    }
  };

  const handleSelectConversation = async (conversationId) => {
    try {
      const conversation = await getConversation(conversationId);
      setSelectedConversation(conversation);
      setHistoryDocument(null);
      setGeneratedNote(null);
      if (conversation.document_id) {
        const document = await getDocument(conversation.document_id);
        setHistoryDocument(document);
        setUploadedDocument(document);
        if (document.notes_id) {
          try {
            setGeneratedNote(await getNote(document.notes_id));
          } catch {
            setGeneratedNote(null);
          }
        }
      }
      setIsHistoryOpen(false);
      setStatusMessage(
        "Conversation and its uploaded file loaded. You can continue chatting.",
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Unable to open conversation.",
      );
    }
  };

  const handleNewConversation = () => {
    setIsSidebarOpen(false);
    setUploadedDocument(null);
    setInstructions("");
    setGeneratedNote(null);
    setHistoryDocument(null);
    setSelectedConversation(null);
    setIsHistoryOpen(false);
    setStatusMessage(
      "New workspace ready. Upload a file or record audio to begin.",
    );
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSendConversationMessage = async (event) => {
    event.preventDefault();
    const content = conversationMessage.trim();
    if (!content || isSendingMessage) return;

    setIsSendingMessage(true);
    try {
      let conversation = selectedConversation;
      if (!conversation) {
        conversation = await createConversation(
          content.slice(0, 80),
          uploadedDocument?.id || null,
        );
      }
      const updated = await sendConversationMessage(conversation.id, content);
      setSelectedConversation(updated);
      setConversationMessage("");
      setConversations((current) => [
        updated,
        ...current.filter((item) => item.id !== updated.id),
      ]);
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Unable to send message.",
      );
    } finally {
      setIsSendingMessage(false);
    }
  };

  const groupConversationsByDay = () => {
    const today = new Date();
    const groups = { Today: [], Yesterday: [] };
    conversations.forEach((conversation) => {
      const date = new Date(conversation.updated_at || conversation.created_at);
      const dayStart = new Date(
        today.getFullYear(),
        today.getMonth(),
        today.getDate(),
      );
      const dateStart = new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate(),
      );
      const difference = Math.round((dayStart - dateStart) / 86400000);
      const label =
        difference === 0
          ? "Today"
          : difference === 1
            ? "Yesterday"
            : date.toLocaleDateString(undefined, { weekday: "long" });
      if (!groups[label]) groups[label] = [];
      groups[label].push(conversation);
    });
    return groups;
  };

  const handleLogout = () => {
    localStorage.removeItem("noteflow_access_token");
    window.location.href = "/";
  };

  const handleUploadFile = async (file) => {
    if (!file) return;

    setIsUploading(true);
    setStatusMessage("Uploading file...");

    try {
      const document = await uploadDocument(file);
      setUploadedDocument(document);
      setStatusMessage("Your file is being processed. Please wait...");
      await waitForDocumentReady(document.id);
      setUploadedDocument((current) => ({
        ...current,
        ...document,
        processing_status: "completed",
      }));
      setHistoryDocument(document);
      setStatusMessage("Your file is ready. You can generate notes now.");
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Unable to upload file.",
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileSelection = (event) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      handleUploadFile(selectedFile);
    }
    event.target.value = "";
  };

  const handleGenerateNotes = async () => {
    if (!uploadedDocument) {
      setStatusMessage(
        "Upload a document or record audio before generating notes.",
      );
      return;
    }

    if (uploadedDocument.processing_status !== "completed") {
      setStatusMessage("Please wait until your file finishes processing.");
      return;
    }

    setIsGenerating(true);
    setStatusMessage("Generating notes...");

    try {
      const generated = await generateNotesForDocument(
        uploadedDocument.id,
        instructions.trim() ||
          "Summarize the content clearly and highlight key study points.",
      );
      setGeneratedNote(generated);
      setStatusMessage("Notes generated successfully.");
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Unable to generate notes.",
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExportNote = async () => {
    if (!generatedNote) return;
    setIsExporting(true);
    try {
      const blob = await exportNote(generatedNote.id, outputFormat);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${generatedNote.title || "study-notes"}.${outputFormat === "plain_text" ? "txt" : outputFormat}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setStatusMessage(`Notes downloaded as ${outputFormat.toUpperCase()}.`);
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Unable to export notes.",
      );
    } finally {
      setIsExporting(false);
    }
  };

  const handleRecordToggle = async () => {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      setStatusMessage("Audio recording is not supported in this browser.");
      return;
    }

    if (isRecording) {
      mediaRecorderRef.current?.stop();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      activeStreamRef.current = stream;
      const recorder = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });

        const recordFile = new File(
          [audioBlob],
          `voice-note-${Date.now()}.webm`,
          {
            type: audioBlob.type || "audio/webm",
          },
        );

        if (activeStreamRef.current) {
          activeStreamRef.current.getTracks().forEach((track) => track.stop());
          activeStreamRef.current = null;
        }

        setIsRecording(false);
        await handleUploadFile(recordFile);
      };

      recorder.start();
      setIsRecording(true);
      setStatusMessage("Recording in progress. Tap again to stop.");
    } catch (error) {
      setStatusMessage(
        error instanceof Error ? error.message : "Unable to access microphone.",
      );
      setIsRecording(false);
    }
  };

  return (
    <div className="app-frame">
      <div className="topbar">
        <div className="topbar-left">
          <button
            className="hamburger"
            type="button"
            aria-label="Toggle sidebar"
            onClick={() => setIsSidebarOpen((open) => !open)}
          >
            <i className="fas fa-bars" />
          </button>
          <div className="logo">
            <div className="logo-icon">
              <i className="fas fa-layer-group" />
            </div>
            NoteFlow
          </div>
        </div>
        <div className="user-info">
          <div className="user-avatar">
            {user?.full_name?.slice(0, 1).toUpperCase() ?? "..."}
          </div>
          <div className="user-name">{user?.full_name ?? "Loading..."}</div>
        </div>
      </div>

      <div className="main-layout">
        <button
          className={`sidebar-backdrop${isSidebarOpen ? " visible" : ""}`}
          type="button"
          aria-label="Close navigation menu"
          tabIndex={isSidebarOpen ? 0 : -1}
          onClick={() => setIsSidebarOpen(false)}
        />
        <aside className={`sidebar${isSidebarOpen ? " open" : ""}`}>
          <button
            className="sidebar-item active"
            type="button"
            onClick={handleNewConversation}
          >
            <i className="fas fa-plus" /> New
          </button>
          <button
            className={`sidebar-item${isHistoryOpen ? " active" : ""}`}
            type="button"
            onClick={handleOpenHistory}
          >
            <i className="fas fa-clock-rotate-left" /> History
          </button>
          {isHistoryOpen && (
            <div className="conversation-history">
              {Object.entries(groupConversationsByDay()).map(
                ([day, items]) =>
                  items.length > 0 && (
                    <section key={day} className="history-group">
                      <h4>{day}</h4>
                      {items.map((conversation) => (
                        <button
                          className="history-conversation"
                          key={conversation.id}
                          type="button"
                          onClick={() =>
                            handleSelectConversation(conversation.id)
                          }
                        >
                          <i className="fas fa-message" />
                          <span>{conversation.title}</span>
                        </button>
                      ))}
                    </section>
                  ),
              )}
              {conversations.length === 0 && (
                <p className="history-empty">No conversations yet.</p>
              )}
            </div>
          )}
          <a
            className="sidebar-item"
            href="/visuals"
            onClick={() => setIsSidebarOpen(false)}
          >
            <i className="fas fa-chart-bar" /> Visuals
          </a>
          <a
            className="sidebar-item"
            href="/settings"
            onClick={() => setIsSidebarOpen(false)}
          >
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

        <main className="main-content">
          <h2 className="create-heading">
            What would you like to <span>create today?</span>
          </h2>

          <div className="create-grid">
            <div className="create-card">
              <div className="card-icon">
                <i className="fas fa-file-arrow-up" />
              </div>
              <h3>Upload File</h3>
              <p>Choose PDF, DOCX, image, audio/video.</p>
              <button
                className="card-btn"
                type="button"
                disabled={isUploading}
                onClick={() => fileInputRef.current?.click()}
              >
                <i className="fas fa-upload" />{" "}
                {isUploading ? "Uploading..." : "Upload"}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.pptx,.png,.jpg,.jpeg,.mp3,.wav,.mp4,.webm"
                hidden
                onChange={handleFileSelection}
              />
            </div>

            <div className="create-card">
              <div className="card-icon">
                <i className="fas fa-microphone" />
              </div>
              <h3>Record Audio</h3>
              <p>Start recording and save as WEBM.</p>
              <button
                className={`card-btn record ${isRecording ? "active" : ""}`}
                type="button"
                onClick={handleRecordToggle}
              >
                <span className="dot" /> {isRecording ? "Stop" : "Record"}
              </button>
            </div>
          </div>

          {uploadedDocument && (
            <div className="upload-status">
              <span
                className={`status-pill ${uploadedDocument.processing_status === "completed" ? "ready" : "processing"}`}
              >
                {uploadedDocument.processing_status === "completed"
                  ? "Ready"
                  : uploadedDocument.processing_status}
              </span>
              <span>{uploadedDocument.file_name}</span>
            </div>
          )}

          <div className="instruction-card">
            <label htmlFor="instruction">User instruction</label>
            <textarea
              id="instruction"
              placeholder="Write additional inforamation..."
              value={instructions}
              onChange={(event) => setInstructions(event.target.value)}
            />
            <div className="generate-row">
              <button
                className="btn-generate"
                type="button"
                onClick={handleGenerateNotes}
                disabled={
                  isGenerating ||
                  isUploading ||
                  uploadedDocument?.processing_status !== "completed"
                }
              >
                <i className="fas fa-pen-to-square" />
                <span>{isGenerating ? "Generating..." : "Generate Notes"}</span>
              </button>
            </div>
          </div>

          {statusMessage && <div className="status-panel">{statusMessage}</div>}

          {selectedConversation && (
            <section className="conversation-panel">
              <div className="conversation-header">
                <div>
                  <span className="conversation-kicker">Conversation</span>
                  <h3>{selectedConversation.title}</h3>
                </div>
                <button
                  type="button"
                  className="conversation-close"
                  onClick={() => setSelectedConversation(null)}
                  aria-label="Close conversation"
                >
                  ×
                </button>
              </div>
              <div className="conversation-messages">
                {selectedConversation.messages?.map((message) => (
                  <div
                    className={`conversation-message ${message.role}`}
                    key={message.id}
                  >
                    <span>
                      {message.role === "user" ? "You" : "NoteFlow AI"}
                    </span>
                    <p>{message.content}</p>
                  </div>
                ))}
              </div>
              <form
                className="conversation-form"
                onSubmit={handleSendConversationMessage}
              >
                <textarea
                  value={conversationMessage}
                  onChange={(event) =>
                    setConversationMessage(event.target.value)
                  }
                  placeholder="Continue this conversation..."
                  rows="2"
                />
                <button
                  type="submit"
                  className="btn-generate"
                  disabled={isSendingMessage || !conversationMessage.trim()}
                >
                  {isSendingMessage ? "Sending..." : "Send"}
                </button>
              </form>
            </section>
          )}

          {generatedNote && (
            <div className="generated-note">
              <h3>Generated Notes</h3>
              <pre>{cleanNoteContent(generatedNote.content)}</pre>
              <div className="export-row">
                <label htmlFor="output-format">Download as</label>
                <select
                  id="output-format"
                  value={outputFormat}
                  onChange={(event) => setOutputFormat(event.target.value)}
                >
                  <option value="pdf">PDF</option>
                  <option value="pptx">PPTX</option>
                  <option value="docx">DOCX</option>
                  <option value="plain_text">Plain text</option>
                </select>
                <button
                  type="button"
                  className="btn-generate"
                  onClick={handleExportNote}
                  disabled={isExporting}
                >
                  {isExporting ? "Preparing..." : "Download"}
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default HomePage;
