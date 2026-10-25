import { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = "https://quepromo.com.br";

  const staticRoutes = [
    "",
    "/ofertas-relampago",
    "/radar",
    "/busca-personalizada",
    "/lojas",
    "/favoritos",
    "/sobre-nos",
    "/contato",
    "/politica-de-privacidade",
    "/termos-de-uso",
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: "hourly" as const,
    priority: route === "" ? 1.0 : 0.8,
  }));

  return staticRoutes;
}
