import type { Deal, StoreItem } from "./api";
import { getDealsPage } from "./server-api";

export interface ShowcaseSection {
  store: string;
  total: number;
  deals: Deal[];
}

// Lojas grandes ganham uma vitrine própria, desde que tenham ofertas suficientes para preencher uma linha.
const SHOWCASE_STORES = ["Amazon", "Mercado Livre", "Magazine Luiza", "KaBuM!"];
export const SHOWCASE_MIN_DEALS = 4;
const SHOWCASE_FETCH = 24;

/** Melhores ofertas de cada loja grande: quedas de preço confirmadas primeiro, depois as mais recentes. */
export async function fetchStoreShowcase(stores: StoreItem[], size: number): Promise<ShowcaseSection[]> {
  const eligible = SHOWCASE_STORES.map((name) => stores.find((store) => store.name === name)).filter(
    (store): store is StoreItem => Boolean(store) && (store as StoreItem).total_deals >= SHOWCASE_MIN_DEALS
  );

  const sections = await Promise.all(
    eligible.map(async (store) => {
      // Uma única chamada por loja; as quedas de preço confirmadas (price_dropped) sobem para o topo.
      const page = await getDealsPage({ limit: SHOWCASE_FETCH, offset: 0, source: store.name });
      const deals = (page?.items ?? [])
        .filter((deal) => deal.image_url)
        .sort((a, b) => (b.price_dropped ? 1 : 0) - (a.price_dropped ? 1 : 0))
        .slice(0, size);
      return { store: store.name, total: store.total_deals, deals };
    })
  );
  return sections.filter((section) => section.deals.length >= SHOWCASE_MIN_DEALS);
}
