import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getDealDetail } from "@/lib/server-api";
import {
  SITE_NAME,
  NOINDEX_METADATA,
  buildBreadcrumbJsonLd,
  buildProductDescription,
  buildProductJsonLd,
  buildProductTitle,
  productPath,
  serializeJsonLd,
} from "@/lib/seo";
import ProductDetailClient from "./ProductDetailClient";

export const revalidate = 600;

interface ProductPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const { id } = await params;
  const deal = await getDealDetail(id);

  if (!deal) {
    return { title: `Oferta não encontrada | ${SITE_NAME}`, ...NOINDEX_METADATA };
  }

  const title = buildProductTitle(deal);
  const description = buildProductDescription(deal);
  const path = productPath(deal.id);
  const images = deal.image_url ? [{ url: deal.image_url, alt: deal.title }] : undefined;

  return {
    title,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "website",
      siteName: SITE_NAME,
      locale: "pt_BR",
      url: path,
      title,
      description,
      images,
    },
    twitter: {
      card: images ? "summary_large_image" : "summary",
      title,
      description,
      images: deal.image_url ? [deal.image_url] : undefined,
    },
  };
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params;
  const deal = await getDealDetail(id);

  if (!deal) notFound();

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: serializeJsonLd(buildProductJsonLd(deal)) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: serializeJsonLd(buildBreadcrumbJsonLd(deal)) }}
      />
      <ProductDetailClient deal={deal} />
    </>
  );
}
