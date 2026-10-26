import type { Metadata } from "next";
import { NOINDEX_METADATA } from "@/lib/seo";

export const metadata: Metadata = {
  title: "Meus Alertas de Preço | Que Promo",
  ...NOINDEX_METADATA,
};

export default function AlertasLayout({ children }: { children: React.ReactNode }) {
  return children;
}
