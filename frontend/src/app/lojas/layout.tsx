import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Lojas Parceiras Monitoradas | Que Promo",
  description:
    "Veja as lojas que o Que Promo monitora, como Amazon, Mercado Livre, Shopee e Magalu, e acesse as ofertas e quedas de preço de cada uma.",
};

export default function LojasLayout({ children }: { children: React.ReactNode }) {
  return children;
}
