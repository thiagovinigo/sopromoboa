import { Deal } from "./api";

const USER_TOKEN_KEY = "sopromoboa_user_token";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export function getUserToken(): string {
  if (typeof window === "undefined") return "";
  let token = localStorage.getItem(USER_TOKEN_KEY);
  if (!token) {
    // Gera token anônimo único de 32 bytes
    token = Array.from(crypto.getRandomValues(new Uint8Array(16)))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    localStorage.setItem(USER_TOKEN_KEY, token);
  }
  return token;
}

export async function fetchFavoriteIds(): Promise<string[]> {
  const token = getUserToken();
  if (!token) return [];

  try {
    const res = await fetch(`${API_BASE}/api/favorites/ids`, {
      headers: { "X-User-Token": token },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Erro ao carregar IDs de favoritos:", err);
    return [];
  }
}

export async function fetchFavorites(): Promise<Deal[]> {
  const token = getUserToken();
  if (!token) return [];

  try {
    const res = await fetch(`${API_BASE}/api/favorites`, {
      headers: { "X-User-Token": token },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Erro ao carregar favoritos:", err);
    return [];
  }
}

export async function toggleFavoriteApi(productId: string): Promise<boolean> {
  const token = getUserToken();
  try {
    const res = await fetch(`${API_BASE}/api/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Token": token,
      },
      body: JSON.stringify({ product_id: productId }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    return Boolean(data.is_favorited);
  } catch (err) {
    console.error("Erro ao alternar favorito:", err);
    return false;
  }
}
