import type { CategoryItem, Deal, DealDetail, StoreItem } from "./api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const REVALIDATE_SECONDS = 600;
const SITEMAP_PAGE_SIZE = 100; // limite máximo aceito por /api/deals
const SITEMAP_CONCURRENCY = 6;
const MAX_SITEMAP_PRODUCTS = 45000; // um sitemap aceita até 50.000 URLs

interface DealsPage {
  items: Deal[];
  total: number;
}

async function fetchFromApi(path: string): Promise<Response | null> {
  try {
    return await fetch(`${API_BASE}${path}`, { next: { revalidate: REVALIDATE_SECONDS } });
  } catch (err) {
    console.error(`[server-api] Falha de rede em ${path}:`, err);
    return null;
  }
}

async function getJson<T>(path: string): Promise<T | null> {
  const res = await fetchFromApi(path);
  if (!res || !res.ok) return null;
  return (await res.json()) as T;
}

/**
 * Retorna null apenas quando a API confirma que o produto não existe (404).
 * Falhas transitórias lançam erro: assim o Google recebe 5xx (e tenta de novo)
 * em vez de um 404 que derrubaria a página do índice.
 */
export async function getDealDetail(id: string): Promise<DealDetail | null> {
  const res = await fetchFromApi(`/api/deals/${encodeURIComponent(id)}`);
  if (!res) throw new Error(`API indisponível ao carregar o produto ${id}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`API respondeu ${res.status} ao carregar o produto ${id}`);
  return (await res.json()) as DealDetail;
}

export async function getDealsPage(params: {
  limit: number;
  offset: number;
  sort?: string;
}): Promise<DealsPage | null> {
  const query = new URLSearchParams({
    limit: String(params.limit),
    offset: String(params.offset),
    sort: params.sort ?? "recent",
  });
  const res = await fetchFromApi(`/api/deals?${query.toString()}`);
  if (!res || !res.ok) return null;
  const total = parseInt(res.headers.get("X-Total-Count") || "0", 10);
  return { items: (await res.json()) as Deal[], total };
}

export function getCategories(): Promise<CategoryItem[] | null> {
  return getJson<CategoryItem[]>("/api/categories");
}

export function getStores(): Promise<StoreItem[] | null> {
  return getJson<StoreItem[]>("/api/stores");
}

function chunk<T>(items: T[], size: number): T[][] {
  const groups: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    groups.push(items.slice(i, i + size));
  }
  return groups;
}

/** Lista id + última atualização de todos os produtos ativos, para o sitemap. */
export async function getSitemapProducts(): Promise<Pick<Deal, "id" | "last_updated">[]> {
  const first = await getDealsPage({ limit: SITEMAP_PAGE_SIZE, offset: 0 });
  if (!first) return [];

  const total = Math.min(first.total, MAX_SITEMAP_PRODUCTS);
  const offsets: number[] = [];
  for (let offset = SITEMAP_PAGE_SIZE; offset < total; offset += SITEMAP_PAGE_SIZE) {
    offsets.push(offset);
  }

  let collected = first.items;
  for (const batch of chunk(offsets, SITEMAP_CONCURRENCY)) {
    const pages = await Promise.all(
      batch.map((offset) => getDealsPage({ limit: SITEMAP_PAGE_SIZE, offset }))
    );
    collected = [...collected, ...pages.flatMap((page) => page?.items ?? [])];
  }

  const uniqueById = new Map(collected.map((deal) => [deal.id, deal]));
  return Array.from(uniqueById.values()).map(({ id, last_updated }) => ({ id, last_updated }));
}
