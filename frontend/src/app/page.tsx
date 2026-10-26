import HomeClient from "@/components/HomeClient";
import { getCategories, getDealsPage, getStores } from "@/lib/server-api";

export const revalidate = 300;

const HOME_PAGE_SIZE = 20;

export default async function HomePage() {
  const [deals, categories, stores] = await Promise.all([
    getDealsPage({ limit: HOME_PAGE_SIZE, offset: 0 }),
    getCategories(),
    getStores(),
  ]);

  return (
    <HomeClient
      initialDeals={deals?.items ?? []}
      initialTotal={deals?.total ?? 0}
      initialCategories={categories ?? []}
      initialStores={stores ?? []}
    />
  );
}
