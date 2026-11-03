const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

function getAuthHeaders(extraHeaders = {}) {
  const token = localStorage.getItem("noteflow_access_token");
  return {
    ...extraHeaders,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function readError(response) {
  const payload = await response.json().catch(() => null);
  if (typeof payload?.detail === "string") return payload.detail;
  if (typeof payload?.message === "string") return payload.message;
  return "Something went wrong. Please try again.";
}

export async function registerUser({ fullName, email, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    body: JSON.stringify({ full_name: fullName, email, password }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function loginUser({ email, password }) {
  const body = new URLSearchParams({ password, username: email });
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    body,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function forgotPassword({ email }) {
  const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
    body: JSON.stringify({ email }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function resetPassword({ token, new_password }) {
  const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
    body: JSON.stringify({ token, new_password }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function getCurrentUser() {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function updateCurrentUser({ fullName, email }) {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    body: JSON.stringify({ full_name: fullName, email }),
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    method: "PUT",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function listDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function getDocument(documentId) {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function getNote(noteId) {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file, file.name);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    body: formData,
    headers: getAuthHeaders(),
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function listConversations() {
  const response = await fetch(`${API_BASE_URL}/conversations`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function createConversation(title = "New conversation", documentId = null) {
  const response = await fetch(`${API_BASE_URL}/conversations`, {
    body: JSON.stringify({ title, document_id: documentId }),
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function getConversation(conversationId) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function sendConversationMessage(conversationId, content) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
    body: JSON.stringify({ content }),
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function exportNote(noteId, format) {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/export`, {
    body: JSON.stringify({ format }),
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.blob();
}

export async function listNotes() {
  const response = await fetch(`${API_BASE_URL}/notes`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function listVisuals(noteId) {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/visuals`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function getVisualFile(visualId, { signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/notes/visuals/${visualId}/file`, {
    headers: getAuthHeaders(),
    signal,
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.blob();
}

export async function generateVisual(noteId, payload) {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/generate-visual`, {
    body: JSON.stringify(payload),
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function generateNotesForDocument(documentId, instruction) {
  const payload = {
    document_id: documentId,
    style: "study_notes",
    language: "en",
    format: "plain_text",
    custom_instruction: instruction || "Summarize the key concepts clearly and make the notes easy to study.",
  };

  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/generate-notes`, {
    body: JSON.stringify(payload),
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    method: "POST",
  });

  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}
