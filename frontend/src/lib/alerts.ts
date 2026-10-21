const ALERT_TOKEN_KEY = "sopromoboa_alert_token";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export function getAlertToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ALERT_TOKEN_KEY);
}

export function setAlertToken(token: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ALERT_TOKEN_KEY, token);
}

export async function createAlert(data: {
  search_term: string;
  target_price?: number;
  min_discount_percent?: number;
  category?: string;
}) {
  const existingToken = getAlertToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (existingToken) {
    headers["X-Alert-Token"] = existingToken;
  }

  const res = await fetch(`${API_BASE}/api/alerts`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });

  const json = await res.json();
  if (json.manage_token) {
    setAlertToken(json.manage_token);
  }
  return json;
}

export async function fetchMyAlerts() {
  const token = getAlertToken();
  if (!token) return [];

  const res = await fetch(`${API_BASE}/api/alerts`, {
    headers: { "X-Alert-Token": token },
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}

export async function deleteAlert(id: number) {
  const token = getAlertToken();
  if (!token) return { success: false };

  const res = await fetch(`${API_BASE}/api/alerts/${id}`, {
    method: "DELETE",
    headers: { "X-Alert-Token": token },
  });
  return res.json();
}
