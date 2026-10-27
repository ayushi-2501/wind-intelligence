
const API_BASE = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/+$/, "");

export async function getJanuaryAnalysis() {
  const response = await fetch(
    `${API_BASE}/api/analysis/january-2026`
  );

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }

  return response.json();
}
