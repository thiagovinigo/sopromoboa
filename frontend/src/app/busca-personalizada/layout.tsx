import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Comparador de Preços entre Lojas | Que Promo",
  description:
    "Pesquise qualquer produto e compare o preço em várias lojas do Brasil para encontrar o menor valor antes de comprar.",
};

export default function BuscaPersonalizadaLayout({ children }: { children: React.ReactNode }) {
  return children;
}
