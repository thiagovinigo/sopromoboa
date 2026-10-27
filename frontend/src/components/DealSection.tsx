import type { ReactNode } from "react";
import type { Deal } from "@/lib/api";
import DealCard from "@/components/DealCard";

interface DealSectionProps {
  title: string;
  icon?: ReactNode;
  deals: Deal[];
  linkHref?: string;
  linkLabel?: string;
  note?: string;
}

/** Linha de ofertas com título, link opcional e nota (ex.: aviso de afiliado). Não usa estado: serve para servidor e cliente. */
export default function DealSection({ title, icon, deals, linkHref, linkLabel, note }: DealSectionProps) {
  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          {icon}
          {title}
        </h2>
        {linkHref && linkLabel && (
          // <a> e não <Link>: o filtro por loja é lido da URL ao carregar a página
          <a href={linkHref} className="text-xs font-semibold text-rose-400 hover:text-rose-300 transition-colors">
            {linkLabel}
          </a>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {deals.map((deal) => (
          <DealCard key={deal.id} deal={deal} />
        ))}
      </div>
      {note && <p className="text-[11px] text-gray-500">{note}</p>}
    </section>
  );
}
