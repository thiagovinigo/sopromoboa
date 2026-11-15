import { MetadataRoute } from "next";
import { getSitemapProducts } from "@/lib/server-api";
import { SITE_URL, parseApiDate, productPath } from "@/lib/seo";

// Gerado sob demanda: no build seriam ~300 chamadas à API de uma vez.
export const dynamic = "force-dynamic";

// Páginas privadas (favoritos, alertas, afiliados, admin) ficam de fora de propósito.
const STATIC_ROUTES = [
  "",
  "/destaques",
  "/radar",
  "/busca-personalizada",
  "/lojas",
  "/sobre-nos",
  "/contato",
  "/politica-de-privacidade",
  "/termos-de-uso",
];

const CACHE_TTL_MS = 60 * 60 * 1000;

interface SitemapCache {
  entries: MetadataRoute.Sitemap;
  builtAt: number;
}

// Cache em memória do processo: a geração fria depende de ~300 chamadas à API e
// pode levar dezenas de segundos com a VPS carregada; o Googlebot não pode esperar isso.
let cache: SitemapCache | null = null;
let inflight: Promise<SitemapCache | null> | null = null;

async function buildEntries(): Promise<MetadataRoute.Sitemap> {
  const staticEntries: MetadataRoute.Sitemap = STATIC_ROUTES.map((route) => ({
    url: `${SITE_URL}${route}`,
  }));

  const products = await getSitemapProducts();
  const productEntries: MetadataRoute.Sitemap = products.map((product) => ({
    url: `${SITE_URL}${productPath(product.id)}`,
    lastModified: parseApiDate(product.last_updated),
  }));

  return [...staticEntries, ...productEntries];
}

/** Reconstrói o cache. Resultado só com páginas estáticas (API falhou) não substitui o anterior. */
function refresh(): Promise<SitemapCache | null> {
  if (inflight) return inflight;
  inflight = buildEntries()
    .then((entries) => {
      if (entries.length > STATIC_ROUTES.length) {
        cache = { entries, builtAt: Date.now() };
      }
      return cache;
    })
    .catch((err: unknown) => {
      console.error("[sitemap] Falha ao gerar o sitemap:", err);
      return cache;
    })
    .finally(() => {
      inflight = null;
    });
  return inflight;
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  if (cache) {
    if (Date.now() - cache.builtAt > CACHE_TTL_MS) void refresh(); // devolve o antigo e atualiza ao fundo
    return cache.entries;
  }

  const built = await refresh();
  if (built) return built.entries;
  return STATIC_ROUTES.map((route) => ({ url: `${SITE_URL}${route}` }));
}
