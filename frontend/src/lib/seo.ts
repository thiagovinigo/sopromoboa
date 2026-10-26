import type { Metadata } from "next";
import type { DealDetail } from "./api";

export const SITE_URL = "https://quepromo.com.br";
export const SITE_NAME = "Que Promo";

const MAX_PRODUCT_NAME_IN_TITLE = 42;
const MAX_DESCRIPTION_LENGTH = 160;

export const NOINDEX_METADATA: Metadata = {
  robots: { index: false, follow: false },
};

export function formatBRL(value: number): string {
  return value
    .toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
    .replace(/ /g, " ");
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  const cut = text.slice(0, maxLength - 1);
  const lastSpace = cut.lastIndexOf(" ");
  const base = lastSpace > maxLength * 0.6 ? cut.slice(0, lastSpace) : cut;
  return `${base.trimEnd()}…`;
}

/** A API devolve datas UTC sem fuso (ex.: 2026-10-26T00:55:40); sem o "Z" o JS as leria como horário local. */
export function parseApiDate(value?: string | null): Date | undefined {
  if (!value) return undefined;
  const hasTimeZone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(value);
  const date = new Date(hasTimeZone ? value : `${value}Z`);
  return Number.isNaN(date.getTime()) ? undefined : date;
}

export function productPath(id: string): string {
  return `/produto/${id}`;
}

export function buildProductTitle(deal: DealDetail): string {
  const name = truncate(deal.title, MAX_PRODUCT_NAME_IN_TITLE);
  return `${name} por ${formatBRL(deal.price)} | ${SITE_NAME}`;
}

export function buildProductDescription(deal: DealDetail): string {
  const discount = deal.discount_percent > 0 ? `, ${Math.round(deal.discount_percent)}% OFF` : "";
  const lowest = deal.is_all_time_low ? " Menor preço já registrado." : "";
  const text =
    `${deal.title} por ${formatBRL(deal.price)} na ${deal.source}${discount}.${lowest} ` +
    `Veja o histórico de preço e compare antes de comprar no ${SITE_NAME}.`;
  return truncate(text, MAX_DESCRIPTION_LENGTH);
}

export function buildProductJsonLd(deal: DealDetail): Record<string, unknown> {
  const url = `${SITE_URL}${productPath(deal.id)}`;
  const hasRating = deal.rating != null && deal.rating > 0 && deal.review_count > 0;

  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: deal.title,
    sku: deal.id,
    url,
    ...(deal.image_url ? { image: [deal.image_url] } : {}),
    ...(deal.brand ? { brand: { "@type": "Brand", name: deal.brand } } : {}),
    ...(hasRating
      ? {
          aggregateRating: {
            "@type": "AggregateRating",
            ratingValue: deal.rating,
            reviewCount: deal.review_count,
          },
        }
      : {}),
    offers: {
      "@type": "Offer",
      url,
      priceCurrency: "BRL",
      price: deal.price.toFixed(2),
      availability: "https://schema.org/InStock",
      itemCondition: "https://schema.org/NewCondition",
      seller: { "@type": "Organization", name: deal.source },
    },
  };
}

export function buildBreadcrumbJsonLd(deal: DealDetail): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Início", item: SITE_URL },
      {
        "@type": "ListItem",
        position: 2,
        name: deal.title,
        item: `${SITE_URL}${productPath(deal.id)}`,
      },
    ],
  };
}

export function buildSiteJsonLd(): Record<string, unknown>[] {
  return [
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      name: SITE_NAME,
      url: SITE_URL,
      logo: `${SITE_URL}/android-chrome-512x512.png`,
      sameAs: ["https://t.me/quepromo"],
    },
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      name: SITE_NAME,
      url: SITE_URL,
      inLanguage: "pt-BR",
      potentialAction: {
        "@type": "SearchAction",
        target: `${SITE_URL}/busca-personalizada?q={search_term_string}`,
        "query-input": "required name=search_term_string",
      },
    },
  ];
}

/** Serializa JSON-LD escapando "<" para impedir que o conteúdo feche a tag <script>. */
export function serializeJsonLd(data: unknown): string {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}
