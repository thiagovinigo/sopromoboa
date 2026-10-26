import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Radar de Quedas de Preço | Que Promo",
  description:
    "Produtos que realmente baixaram de preço nos últimos dias nas principais lojas do Brasil, com histórico auditado e comparação com o preço anterior.",
};

export default function RadarLayout({ children }: { children: React.ReactNode }) {
  return children;
}
