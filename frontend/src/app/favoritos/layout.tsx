import type { Metadata } from "next";
import { NOINDEX_METADATA } from "@/lib/seo";

export const metadata: Metadata = {
  title: "Meus Favoritos | Que Promo",
  ...NOINDEX_METADATA,
};

export default function FavoritosLayout({ children }: { children: React.ReactNode }) {
  return children;
}
