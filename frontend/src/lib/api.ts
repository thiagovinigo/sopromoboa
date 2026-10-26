export interface PriceHistoryPoint {
  price: number;
  seen_at: string;
}

export interface Deal {
  id: string;
  title: string;
  price: number;
  list_price?: number | null;
  previous_price?: number | null;
  lowest_historic_price?: number | null;
  price_dropped: number;
  discount_percent: number;
  brand?: string | null;
  category: string;
  source: string;
  image_url?: string | null;
  url: string;
  affiliate_url?: string | null;
  coupon_code?: string | null;
  free_shipping: number;
  rating?: number | null;
  review_count: number;
  is_all_time_low: boolean;
  is_affiliate_deal?: number;
  is_featured?: number;
  is_lightning_deal?: number;
  clicks_count?: number;
  last_updated: string;
}

export interface DealDetail extends Deal {
  price_history: PriceHistoryPoint[];
  similar_deals: Deal[];
}

export interface CategoryItem {
  slug: string;
  name: string;
  total_deals: number;
}

export interface StoreItem {
  slug: string;
  name: string;
  total_deals: number;
  affiliate_network?: string | null;
}

export interface AffiliateProgram {
  id: number;
  name: string;
  network_slug: string;
  tracking_id: string;
  commission_rate?: string | null;
  status: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const ADMIN_TOKEN_KEY = "sopromoboa_admin_token";

export function getAdminToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(ADMIN_TOKEN_KEY);
}

export function setAdminToken(token: string): void {
  sessionStorage.setItem(ADMIN_TOKEN_KEY, token);
}

export function clearAdminToken(): void {
  sessionStorage.removeItem(ADMIN_TOKEN_KEY);
}

/** fetch para rotas administrativas: anexa o token da sessão do painel. */
function adminFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const token = getAdminToken();
  const headers: Record<string, string> = {
    ...((init.headers as Record<string, string> | undefined) ?? {}),
    ...(token ? { "X-Admin-Token": token } : {}),
  };
  return fetch(input, { ...init, headers });
}

export async function fetchDeals(params: {
  q?: string;
  category?: string;
  source?: string;
  only_drops?: boolean;
  sort?: string;
  limit?: number;
  offset?: number;
}): Promise<{ items: Deal[]; total: number }> {
  const query = new URLSearchParams();
  if (params.q) query.set("q", params.q);
  if (params.category) query.set("category", params.category);
  if (params.source) query.set("source", params.source);
  if (params.only_drops) query.set("only_drops", "true");
  if (params.sort) query.set("sort", params.sort);
  query.set("limit", String(params.limit || 24));
  query.set("offset", String(params.offset || 0));

  try {
    const res = await fetch(`${API_BASE}/api/deals?${query.toString()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Falha ao carregar ofertas");
    const total = parseInt(res.headers.get("X-Total-Count") || "0", 10);
    const items = await res.json();
    return { items, total };
  } catch (err) {
    console.error("Erro na busca de ofertas:", err);
    return { items: [], total: 0 };
  }
}

export async function fetchRadarDeals(): Promise<Deal[]> {
  try {
    const res = await fetch(`${API_BASE}/api/radar`, { cache: "no-store" });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Erro ao buscar radar:", err);
    return [];
  }
}

export async function fetchDealDetail(id: string): Promise<DealDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/api/deals/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error("Erro ao carregar detalhes:", err);
    return null;
  }
}

export async function fetchCategories(): Promise<CategoryItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/categories`, { cache: "no-store" });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function fetchStores(): Promise<StoreItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/stores`, { cache: "no-store" });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function fetchAffiliates(): Promise<AffiliateProgram[]> {
  try {
    const res = await adminFetch(`${API_BASE}/api/affiliates`, { cache: "no-store" });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function saveAffiliate(data: {
  name: string;
  network_slug: string;
  tracking_id: string;
  commission_rate?: string;
}) {
  const res = await adminFetch(`${API_BASE}/api/affiliates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function generateAffiliateLink(url: string, campaign?: string) {
  const res = await fetch(`${API_BASE}/api/affiliates/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, campaign }),
  });
  return res.json();
}

export async function fetchAdminDeals(): Promise<Deal[]> {
  try {
    const res = await adminFetch(`${API_BASE}/api/admin/deals`, { cache: "no-store" });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Erro ao carregar anúncios admin:", err);
    return [];
  }
}

export async function createAdminDeal(data: {
  title: string;
  price: number;
  list_price?: number;
  source?: string;
  url: string;
  image_url?: string;
  category?: string;
  brand?: string;
  coupon_code?: string;
  is_featured?: number;
  is_lightning_deal?: number;
  free_shipping?: number;
}): Promise<Deal | null> {
  try {
    const res = await adminFetch(`${API_BASE}/api/admin/deals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error("Erro ao cadastrar anúncio admin:", err);
    return null;
  }
}

export async function deleteAdminDeal(productId: string): Promise<boolean> {
  try {
    const res = await adminFetch(`${API_BASE}/api/admin/deals/${productId}`, {
      method: "DELETE",
    });
    return res.ok;
  } catch (err) {
    return false;
  }
}

export interface AdminStats {
  total_clicks: number;
  affiliate_deals_count: number;
  total_deals_monitored: number;
  clicks_by_store: { store: string; clicks: number }[];
  top_clicked_deals: { id: string; title: string; clicks: number; price: number; source: string }[];
}

export async function fetchAdminStats(): Promise<AdminStats | null> {
  try {
    const res = await adminFetch(`${API_BASE}/api/admin/stats`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export interface WorkerHistoryItem {
  timestamp: string;
  duration_seconds: number;
  type: string;
  stats: {
    inserted: number;
    updated: number;
    price_drops: number;
    alerts_triggered: number;
  };
}

export interface WorkerStatus {
  is_running: boolean;
  last_run: string | null;
  last_stats: {
    inserted: number;
    updated: number;
    price_drops: number;
    alerts_triggered: number;
  } | null;
  history: WorkerHistoryItem[];
  interval_minutes: number;
  total_monitored: number;
  total_active_drops: number;
  active_scrapers: {
    name: string;
    target: string;
    status: string;
    interval: string;
  }[];
}

export async function fetchWorkerStatus(): Promise<WorkerStatus | null> {
  try {
    const res = await adminFetch(`${API_BASE}/api/worker/status`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error("Erro ao carregar status do worker:", err);
    return null;
  }
}

export async function triggerWorker() {
  const res = await adminFetch(`${API_BASE}/api/worker/run`, { method: "POST" });
  return res.json();
}

export async function simulatePriceDrop() {
  const res = await adminFetch(`${API_BASE}/api/worker/simulate-drop`, { method: "POST" });
  return res.json();
}

export interface StorePriceComparison {
  store: string;
  price: number;
  deal_id: string;
  product_title: string;
  url: string;
  affiliate_url?: string | null;
  image_url?: string | null;
  is_lowest: boolean;
  price_diff: number;
  free_shipping: number;
}

export interface WorkerSearchResult {
  query: string;
  total_found: number;
  best_price?: number | null;
  max_price?: number | null;
  average_price?: number | null;
  potential_savings?: number | null;
  best_store?: string | null;
  did_you_mean?: string | null;
  did_you_mean_notice?: string | null;
  stores_comparison: StorePriceComparison[];
  items: Deal[];
}

export async function fetchComparatorSearch(q: string): Promise<WorkerSearchResult> {
  try {
    const res = await fetch(`${API_BASE}/api/comparator/search?q=${encodeURIComponent(q)}`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Falha na busca personalizada");
    return await res.json();
  } catch (err) {
    console.error("Erro na busca personalizada:", err);
    return {
      query: q,
      total_found: 0,
      stores_comparison: [],
      items: [],
    };
  }
}

// ==========================================
// STORE HUNTER AI AGENT INTERFACES & CALLS
// ==========================================
export interface DiscoveredStore {
  id: number;
  slug: string;
  name: string;
  domain: string;
  official_url: string;
  logo_url?: string | null;
  category: string;
  reclame_aqui_score?: number | null;
  reclame_aqui_badge?: string | null;
  reclame_aqui_resolved_rate?: number | null;
  trust_score: number;
  affiliate_network?: string | null;
  estimated_commission?: string | null;
  affiliate_program_url?: string | null;
  status: "pending" | "approved" | "rejected";
  discovered_reason?: string | null;
  discovered_at?: string | null;
  reviewed_at?: string | null;
}

export interface HunterStats {
  total_discovered: number;
  pending_approval: number;
  approved: number;
  rejected: number;
  average_trust_score: number;
  average_reclame_aqui: number;
}

export async function fetchHunterStores(
  status: string = "all",
  category?: string,
  search?: string
): Promise<DiscoveredStore[]> {
  try {
    const params = new URLSearchParams();
    if (status && status !== "all") params.append("status", status);
    if (category && category !== "all") params.append("category", category);
    if (search) params.append("search", search);

    const res = await adminFetch(`${API_BASE}/api/agent/hunter/stores?${params.toString()}`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Falha ao buscar lojas descobertas");
    return await res.json();
  } catch (err) {
    console.error("Erro fetchHunterStores:", err);
    return [];
  }
}

export async function fetchHunterStats(): Promise<HunterStats | null> {
  try {
    const res = await adminFetch(`${API_BASE}/api/agent/hunter/stats`, { cache: "no-store" });
    if (!res.ok) throw new Error("Falha ao buscar stats do hunter");
    return await res.json();
  } catch (err) {
    console.error("Erro fetchHunterStats:", err);
    return null;
  }
}

export async function runHunterCycle(): Promise<any> {
  const res = await adminFetch(`${API_BASE}/api/agent/hunter/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Falha ao acionar varredura do caçador de lojas");
  return await res.json();
}

export async function approveHunterStore(storeId: number): Promise<any> {
  const res = await adminFetch(`${API_BASE}/api/agent/hunter/stores/${storeId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Falha ao aprovar loja");
  return await res.json();
}

export async function rejectHunterStore(storeId: number): Promise<any> {
  const res = await adminFetch(`${API_BASE}/api/agent/hunter/stores/${storeId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Falha ao rejeitar loja");
  return await res.json();
}

export async function auditCustomStoreUrl(url: string, storeName?: string): Promise<any> {
  const res = await adminFetch(`${API_BASE}/api/agent/hunter/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, store_name: storeName }),
  });
  if (!res.ok) throw new Error("Falha ao auditar URL");
  return await res.json();
}

export async function authenticateAdmin(password: string): Promise<{ success: boolean; token?: string; message?: string }> {
  try {
    const res = await fetch(`${API_BASE}/api/admin/auth`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (res.status === 503) {
      return { success: false, message: "Painel administrativo desativado no servidor." };
    }
    if (!res.ok) {
      return { success: false, message: "Senha incorreta. Acesso não autorizado." };
    }
    const data = await res.json();
    if (data.token) setAdminToken(data.token);
    return data;
  } catch {
    return { success: false, message: "Não foi possível falar com o servidor. Tente novamente." };
  }
}

export async function fetchLightningDeals(params: {
  q?: string;
  category?: string;
  min_discount?: number;
  sort?: string;
  limit?: number;
  offset?: number;
}): Promise<{ items: Deal[]; total: number }> {
  const query = new URLSearchParams();
  if (params.q) query.set("q", params.q);
  if (params.category && params.category !== "todas") query.set("category", params.category);
  if (params.min_discount) query.set("min_discount", String(params.min_discount));
  if (params.sort) query.set("sort", params.sort);
  query.set("limit", String(params.limit || 24));
  query.set("offset", String(params.offset || 0));

  try {
    const res = await fetch(`${API_BASE}/api/deals/lightning?${query.toString()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Falha ao carregar ofertas relâmpago");
    const total = parseInt(res.headers.get("X-Total-Count") || "0", 10);
    const items = await res.json();
    return { items, total };
  } catch (err) {
    console.error("Erro ao buscar ofertas relâmpago:", err);
    return { items: [], total: 0 };
  }
}

export async function triggerLightningScan(): Promise<{
  success: boolean;
  message: string;
  total_active_lightning: number;
}> {
  try {
    const res = await adminFetch(`${API_BASE}/api/deals/lightning/scan`, { method: "POST" });
    if (!res.ok) throw new Error("Falha ao acionar robô");
    return await res.json();
  } catch (err) {
    console.error("Erro ao disparar varredura de ofertas relâmpago:", err);
    return {
      success: false,
      message: "Erro ao comunicar com o robô de ofertas relâmpago",
      total_active_lightning: 0,
    };
  }
}

export async function fetchLightningRobotStatus(): Promise<any> {
  try {
    const res = await adminFetch(`${API_BASE}/api/deals/lightning/robot-status`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function triggerLightningRobotRun(): Promise<any> {
  try {
    const res = await adminFetch(`${API_BASE}/api/deals/lightning/robot-run`, { method: "POST" });
    return await res.json();
  } catch (err) {
    return { success: false, message: "Erro ao comunicar com o robô" };
  }
}

export async function quickImportDeal(payload: {
  url: string;
  custom_title?: string;
  custom_price?: number;
  custom_list_price?: number;
  image_url?: string;
  category?: string;
  coupon_code?: string;
  is_lightning?: boolean;
  is_featured?: boolean;
}): Promise<Deal> {
  const res = await adminFetch(`${API_BASE}/api/admin/quick-import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Falha ao importar anúncio");
  }
  return await res.json();
}



