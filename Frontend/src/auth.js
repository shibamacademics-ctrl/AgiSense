const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "agrisense_access_token";

async function parseResponse(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Request failed with status ${response.status}`);
  return body;
}

export function getToken() { return localStorage.getItem(TOKEN_KEY); }
export function clearToken() { localStorage.removeItem(TOKEN_KEY); }
function saveAuth(body) { localStorage.setItem(TOKEN_KEY, body.access_token); return body; }

export function login(credentials) {
  return fetch(`${API_BASE}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(credentials) }).then(parseResponse).then(saveAuth);
}

export function register(details) {
  return fetch(`${API_BASE}/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(details) }).then(parseResponse).then(saveAuth);
}

export function getCurrentUser() {
  const token = getToken();
  if (!token) return Promise.reject(new Error("Not signed in"));
  return fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } }).then(parseResponse);
}
