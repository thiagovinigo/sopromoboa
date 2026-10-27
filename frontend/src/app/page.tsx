import HomeClient from "@/components/HomeClient";
import type { Deal, StoreItem } from "@/lib/api";
import { pickFeatured } from "@/lib/featured";
import { getCategories, getDealsPage, getStores } from "@/lib/server-api";
import { fetchStoreShowcase } from "@/lib/showcase";

export const revalidate = 300;

const HOME_PAGE_SIZE = 20;
const POOL_MIN_STORE_DEALS = 20;
const POOL_MAX_STORES = 12;
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

const HOME_SHOWCASE_SIZE = 4;

export default async function HomePage() {
  const [recent, categories, stores] = await Promise.all([
    getDealsPage({ limit: HOME_PAGE_SIZE, offset: 0 }),
    getCategories(),
    getStores(),
  ]);

  const [pool, showcase] = await Promise.all([fetchFeaturedPool(stores ?? []), fetchStoreShowcase(stores ?? [], HOME_SHOWCASE_SIZE)]);
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
