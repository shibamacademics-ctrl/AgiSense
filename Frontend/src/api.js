const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function parseResponse(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail || body.message || `Request failed with status ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 60000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The disease model did not respond within 90 seconds. Check the backend terminal for the TensorFlow error.");
    }
    throw new Error("Cannot reach the FastAPI backend. Confirm it is running at http://127.0.0.1:8000.");
  } finally {
    clearTimeout(timeout);
  }
}

export function recommendCrop(payload, farmerId) {
  return fetchWithTimeout(`${API_BASE}/recommend-crop`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(farmerId ? { "X-Farmer-ID": farmerId } : {}) },
    body: JSON.stringify(payload),
  }).then(parseResponse);
}

export function predictYield(payload, farmerId) {
  return fetchWithTimeout(`${API_BASE}/predict-yield`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(farmerId ? { "X-Farmer-ID": farmerId } : {}) },
    body: JSON.stringify(payload),
  }).then(parseResponse);
}

export function detectDisease(file, farmerId) {
  const body = new FormData();
  body.append("file", file);
  return fetchWithTimeout(`${API_BASE}/detect-disease`, {
    method: "POST",
    headers: farmerId ? { "X-Farmer-ID": farmerId } : {},
    body,
  }, 90000).then(parseResponse);
}

export function getHistory(farmerId, limit = 20) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (farmerId) params.set("farmer_id", farmerId);
  return fetch(`${API_BASE}/farmer-queries?${params}`).then(parseResponse);
}

export function getHealth() {
  return fetch(`${API_BASE}/health`).then(parseResponse);
}
