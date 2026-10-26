import { MetadataRoute } from "next";
import { getSitemapProducts } from "@/lib/server-api";
import { SITE_URL, parseApiDate, productPath } from "@/lib/seo";

export const revalidate = 3600;

// Páginas privadas (favoritos, alertas, afiliados, admin) ficam de fora de propósito.
const STATIC_ROUTES = [
  "",
  "/ofertas-relampago",
  "/radar",
  "/busca-personalizada",
  "/lojas",
  "/sobre-nos",
  "/contato",
  "/politica-de-privacidade",
  "/termos-de-uso",
];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
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
