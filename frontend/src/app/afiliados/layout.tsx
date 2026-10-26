import type { Metadata } from "next";
import { NOINDEX_METADATA } from "@/lib/seo";

export const metadata: Metadata = {
  title: "Gerador de Links | Que Promo",
  ...NOINDEX_METADATA,
};

export default function AfiliadosLayout({ children }: { children: React.ReactNode }) {
  return children;
}
