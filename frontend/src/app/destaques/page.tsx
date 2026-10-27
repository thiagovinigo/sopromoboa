import type { Metadata } from "next";
import Link from "next/link";
import { Flame, Store, TrendingDown, Zap } from "lucide-react";
import DealSection from "@/components/DealSection";
import { affiliateNote } from "@/lib/affiliate-note";
import { fetchStoreShowcase, SHOWCASE_MIN_DEALS } from "@/lib/showcase";
import { getDealsPage, getPopularDeals, getStores } from "@/lib/server-api";

export const revalidate = 300;

export const metadata: Metadata = {
  title: "Destaques: Amazon, quedas de preço e mais clicados | Que Promo",
  description:
    "As ofertas em destaque das lojas grandes, as quedas de preço confirmadas pelo radar e as ofertas mais clicadas da semana no Que Promo.",
};

const SECTION_SIZE = 8;
const LIST_SIZE = 12;
const POPULAR_DAYS = 7;

export default async function DestaquesPage() {
  const stores = (await getStores()) ?? [];
  const [storeSections, drops, popular] = await Promise.all([
    fetchStoreShowcase(stores, SECTION_SIZE),
    getDealsPage({ limit: LIST_SIZE, offset: 0, sort: "drop_desc", onlyDrops: true }),
    getPopularDeals(POPULAR_DAYS, LIST_SIZE),
  ]);

  const dropDeals = (drops?.items ?? []).filter((deal) => deal.image_url);
  const showDrops = dropDeals.length >= SHOWCASE_MIN_DEALS;
  const showPopular = popular.length >= SHOWCASE_MIN_DEALS;
  const hasContent = storeSections.length > 0 || showDrops || showPopular;

  return (
    <div className="space-y-8">
      <section className="rounded-3xl p-6 sm:p-8 border border-white/[0.07] bg-[#0d131f]">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold">
          <Zap className="w-3.5 h-3.5" /> Destaques
        </div>
        <h1 className="mt-3 text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          O que merece o seu clique agora
        </h1>
        <p className="mt-2 text-sm text-gray-400 max-w-2xl">
          Ofertas das lojas grandes com link direto, quedas de preço confirmadas pelo nosso radar e o que os
          visitantes mais clicaram esta semana.{" "}
          <Link href="/" className="text-rose-400 hover:text-rose-300 font-semibold">
            Ver todas as ofertas
          </Link>
        </p>
      </section>

      {storeSections.map((section) => (
        <DealSection
          key={section.store}
          title={`Em destaque: ${section.store}`}
          icon={<Store className="w-5 h-5 text-rose-500" />}
          deals={section.deals}
          linkHref={`/?source=${encodeURIComponent(section.store)}`}
          linkLabel={`Ver todas (${section.total})`}
          note={affiliateNote(section.store)}
        />
      ))}

      {showDrops && (
        <DealSection
          title="Quedas de preço confirmadas"
          icon={<TrendingDown className="w-5 h-5 text-rose-500" />}
          deals={dropDeals.slice(0, LIST_SIZE)}
          note="Queda registrada pelo radar entre duas varreduras do mesmo produto."
        />
      )}

      {showPopular && (
        <DealSection
          title={`Mais clicados nos últimos ${POPULAR_DAYS} dias`}
          icon={<Flame className="w-5 h-5 text-amber-400" />}
          deals={popular}
          note="Ranking calculado com os cliques dos visitantes do Que Promo."
        />
      )}

      {!hasContent && (
        <div className="glass-card rounded-3xl p-10 text-center text-sm text-gray-400">
          Ainda estamos reunindo os destaques. Veja <Link href="/" className="text-rose-400">todas as ofertas</Link>.
        </div>
      )}
    </div>
  );
}
