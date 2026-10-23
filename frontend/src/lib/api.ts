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
    const res = await fetch(`${API_BASE}/api/affiliates`, { cache: "no-store" });
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
  const res = await fetch(`${API_BASE}/api/affiliates`, {
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
    const res = await fetch(`${API_BASE}/api/admin/deals`, { cache: "no-store" });
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
  free_shipping?: number;
}): Promise<Deal | null> {
  try {
    const res = await fetch(`${API_BASE}/api/admin/deals`, {
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
    const res = await fetch(`${API_BASE}/api/admin/deals/${productId}`, {
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
    const res = await fetch(`${API_BASE}/api/admin/stats`, { cache: "no-store" });
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
    const res = await fetch(`${API_BASE}/api/worker/status`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error("Erro ao carregar status do worker:", err);
    return null;
  }
}

export async function triggerWorker() {
  const res = await fetch(`${API_BASE}/api/worker/run`, { method: "POST" });
  return res.json();
}

export async function simulatePriceDrop() {
  const res = await fetch(`${API_BASE}/api/worker/simulate-drop`, { method: "POST" });
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

