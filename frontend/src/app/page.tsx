import HomeClient, { ShowcaseSection } from "@/components/HomeClient";
import type { Deal, StoreItem } from "@/lib/api";
import { pickFeatured } from "@/lib/featured";
import { getCategories, getDealsPage, getStores } from "@/lib/server-api";

export const revalidate = 300;

const HOME_PAGE_SIZE = 20;
const POOL_MIN_STORE_DEALS = 20;
const POOL_MAX_STORES = 24;
const POOL_PER_STORE = 40;
const POOL_MIN_DISCOUNT = 20;

/** Amostra das melhores ofertas de cada loja grande, para a vitrine não ficar refém de uma só loja. */
async function fetchFeaturedPool(stores: StoreItem[]): Promise<Deal[]> {
  const names = stores
    .filter((store) => store.total_deals >= POOL_MIN_STORE_DEALS)
    .sort((a, b) => b.total_deals - a.total_deals)
    .slice(0, POOL_MAX_STORES)
    .map((store) => store.name);

  const pages = await Promise.all(
    names.map((source) =>
      getDealsPage({ limit: POOL_PER_STORE, offset: 0, source, minDiscount: POOL_MIN_DISCOUNT })
    )
  );
  return pages.flatMap((page) => page?.items ?? []);
}

// Lojas grandes ganham uma vitrine própria, desde que tenham ofertas suficientes para preencher uma linha.
const SHOWCASE_STORES = ["Amazon", "Mercado Livre", "Magazine Luiza", "KaBuM!"];
const SHOWCASE_MIN_DEALS = 4;
const SHOWCASE_FETCH = 16;
const SHOWCASE_SIZE = 4;

async function fetchShowcase(stores: StoreItem[]): Promise<ShowcaseSection[]> {
  const eligible = SHOWCASE_STORES.map((name) => stores.find((store) => store.name === name)).filter(
    (store): store is StoreItem => Boolean(store) && (store as StoreItem).total_deals >= SHOWCASE_MIN_DEALS
  );

  const sections = await Promise.all(
    eligible.map(async (store) => {
      // Quedas de preço confirmadas primeiro; o restante vem das ofertas mais recentes da loja.
      const [drops, recent] = await Promise.all([
        getDealsPage({ limit: SHOWCASE_SIZE, offset: 0, source: store.name, onlyDrops: true }),
        getDealsPage({ limit: SHOWCASE_FETCH, offset: 0, source: store.name }),
      ]);
      const unique = new Map<string, Deal>();
      for (const deal of [...(drops?.items ?? []), ...(recent?.items ?? [])]) {
        if (deal.image_url && !unique.has(deal.id)) unique.set(deal.id, deal);
      }
      return { store: store.name, total: store.total_deals, deals: Array.from(unique.values()).slice(0, SHOWCASE_SIZE) };
    })
  );
  return sections.filter((section) => section.deals.length >= SHOWCASE_MIN_DEALS);
}

export default async function HomePage() {
  const [recent, categories, stores] = await Promise.all([
    getDealsPage({ limit: HOME_PAGE_SIZE, offset: 0 }),
    getCategories(),
    getStores(),
  ]);

  const [pool, showcase] = await Promise.all([fetchFeaturedPool(stores ?? []), fetchShowcase(stores ?? [])]);
  const featured = pickFeatured(pool, HOME_PAGE_SIZE);
  const useFeatured = featured.length >= HOME_PAGE_SIZE / 2;

  return (
    <HomeClient
      initialDeals={useFeatured ? featured : recent?.items ?? []}
      initialTotal={recent?.total ?? 0}
      initialSort={useFeatured ? "featured" : "recent"}
      showcase={showcase}
      initialCategories={categories ?? []}
      initialStores={stores ?? []}
    />
  );
}
