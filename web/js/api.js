const API_BASE = "http://127.0.0.1:5000";

async function fetchGeneratedParams(payload) {
  const response = await fetch(`${API_BASE}/api/generate-params`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to generate parameters");
  }
  return response.json();
}

async function fetchConfig() {
  const response = await fetch(`${API_BASE}/api/config`);
  if (!response.ok) {
    throw new Error("Failed to load configuration data from backend");
  }
  return response.json();
}

async function fetchSavedScripts() {
  const response = await fetch(`${API_BASE}/api/saved-scripts`);
  if (!response.ok) {
    throw new Error("Failed to load saved scripts");
  }
  return response.json();
}

async function fetchSavedResults() {
  const response = await fetch(`${API_BASE}/api/saved-results`);
  if (!response.ok) {
    throw new Error("Failed to load saved results");
  }
  return response.json();
}

async function generateScript(payload) {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  return response.json();
}

async function saveScript(payload) {
  const response = await fetch(`${API_BASE}/api/save`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to save script");
  }
  return response.json();
}

async function runTest(payload) {
  const response = await fetch(`${API_BASE}/api/run-test`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to run test");
  }
  return response.json();
}

async function saveResults(payload) {
  const response = await fetch(`${API_BASE}/api/save-results`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to save results");
  }
  return response.json();
}

async function deleteResults(payload) {
  const response = await fetch(`${API_BASE}/api/delete-results`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to delete results");
  }
  return response.json();
}

async function analyzeResults(payload) {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to analyze results");
  }
  return response.json();
}

async function saveAnalysisReport(payload) {
  const response = await fetch(`${API_BASE}/api/save-analysis`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to save analysis");
  }
  return response.json();
}