"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ExternalLink,
  TrendingDown,
  Star,
  Zap,
  Ticket,
  Bot,
  Flame,
  Smartphone,
  Laptop,
  Gamepad2,
  Tv,
  ShoppingBag,
  Sparkles
} from "lucide-react";
import { Deal } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

interface DealCardProps {
  deal: Deal;
  isFavorited?: boolean;
  onOpenAlertModal?: (deal: Deal) => void;
  onFavoriteChange?: (dealId: string, isFav: boolean) => void;
}

export default function DealCard({
  deal,
  isFavorited: initialFav = false,
  onOpenAlertModal,
  onFavoriteChange,
}: DealCardProps) {
  const [copiedCoupon, setCopiedCoupon] = useState(false);
  const [isFav, setIsFav] = useState(initialFav);
  const [favLoading, setFavLoading] = useState(false);
  const [imgError, setImgError] = useState(false);

  React.useEffect(() => {
    setIsFav(initialFav);
  }, [initialFav]);

  const handleToggleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (favLoading) return;

    setFavLoading(true);
    const nextState = !isFav;
    setIsFav(nextState);

    try {
      const { toggleFavoriteApi } = await import("@/lib/favorites");
      const res = await toggleFavoriteApi(deal.id);
      setIsFav(res);
      if (onFavoriteChange) onFavoriteChange(deal.id, res);
    } catch {
      setIsFav(!nextState);
    } finally {
      setFavLoading(false);
    }
  };

  const handleCopyCoupon = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (deal.coupon_code) {
      navigator.clipboard.writeText(deal.coupon_code);
      setCopiedCoupon(true);
      setTimeout(() => setCopiedCoupon(false), 2000);
    }
  };

  const getStoreBadgeColor = (source: string) => {
    const s = (source || "").toLowerCase();
    if (s.includes("amazon")) return "bg-amber-500/10 text-amber-400 border-amber-500/30";
    if (s.includes("mercado")) return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
    if (s.includes("magalu") || s.includes("magazine")) return "bg-blue-500/10 text-blue-400 border-blue-500/30";
    if (s.includes("kabum")) return "bg-orange-500/10 text-orange-400 border-orange-500/30";
    return "bg-gray-800 text-gray-300 border-gray-700";
  };

  const getCategoryIcon = (category: string) => {
    const c = (category || "").toLowerCase();
    if (c.includes("smart") || c.includes("celular")) return Smartphone;
    if (c.includes("info") || c.includes("pc") || c.includes("note")) return Laptop;
    if (c.includes("game") || c.includes("consol")) return Gamepad2;
    if (c.includes("eletro") || c.includes("tv") || c.includes("audio")) return Tv;
    return ShoppingBag;
  };

  const formatBRL = (val: number) => {
    return val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  };

  const CategoryIconComponent = getCategoryIcon(deal.category);

  return (
    <div className="glass-card rounded-2xl overflow-hidden flex flex-col transition-all duration-300 hover:-translate-y-1 hover:border-white/20 group relative bg-[#0d131f] border border-white/[0.07]">
      {/* Badges superiores */}
      <div className="absolute top-2.5 left-2.5 z-20 flex flex-wrap gap-1.5 items-center pointer-events-none">
        {deal.discount_percent > 0 && (
          <span className="px-2 py-0.5 text-xs font-bold text-white bg-rose-600 rounded-md shadow-sm flex items-center gap-0.5">
            -{deal.discount_percent}%
          </span>
        )}
        {deal.is_all_time_low && (
          <span className="px-2 py-0.5 text-[10px] font-bold text-emerald-300 bg-emerald-950/80 border border-emerald-500/30 rounded-md">
            Menor Preço
          </span>
        )}
      </div>

      {/* Ações superiores: Favoritar */}
      <div className="absolute top-2.5 right-2.5 z-20 flex items-center gap-1.5">
        <button
          onClick={handleToggleFavorite}
          title={isFav ? "Remover dos favoritos" : "Salvar nos favoritos"}
          className={`p-1.5 rounded-full backdrop-blur-md transition-all ${
            isFav
              ? "bg-rose-600 text-white shadow-md scale-105"
              : "bg-black/40 text-gray-400 hover:text-rose-400 hover:bg-black/60 border border-white/10"
          }`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill={isFav ? "currentColor" : "none"}
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="w-3.5 h-3.5"
          >
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
          </svg>
        </button>

        <Link
          href={`/busca-personalizada?q=${encodeURIComponent(deal.title)}`}
          title="Comparar preços em todas as lojas"
          className="p-1.5 rounded-full bg-black/40 hover:bg-black/60 text-gray-400 hover:text-cyan-400 border border-white/10 transition-colors"
        >
          <Bot className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Imagem do Produto */}
      <Link
        href={`/produto/${deal.id}`}
        className="block relative pt-[70%] bg-[#080d17] overflow-hidden"
      >
        {deal.image_url && !imgError ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={deal.image_url}
            alt=""
            aria-label={deal.title}
            onError={() => setImgError(true)}
            className="absolute inset-0 w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center select-none bg-[#080d17]">
            <div className="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center mb-1.5">
              <CategoryIconComponent className="w-5 h-5 text-gray-400" />
            </div>
            <span className="text-[11px] font-bold text-gray-300 uppercase tracking-wider">{deal.source}</span>
            <span className="text-[10px] text-gray-500 font-medium line-clamp-1 max-w-[85%] mt-0.5">
              {deal.brand || deal.category}
            </span>
          </div>
        )}
      </Link>

      {/* Conteúdo */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          {/* Loja & Avaliação */}
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold text-gray-300 bg-white/[0.04] border border-white/[0.07]">
              {deal.source}
            </span>
            {deal.rating ? (
              <span className="flex items-center gap-1 text-amber-400 font-medium text-xs">
                <Star className="w-3 h-3 fill-amber-400" />
                {deal.rating} {deal.review_count > 0 && `(${deal.review_count})`}
              </span>
            ) : (
              <span className="text-[10px] text-gray-500 uppercase tracking-wider">{deal.category}</span>
            )}
          </div>

          {/* Título com altura fixa de 2 linhas */}
          <Link href={`/produto/${deal.id}`}>
            <h3 className="font-semibold text-sm text-gray-100 hover:text-rose-400 line-clamp-2 h-10 transition-colors mb-2 leading-snug">
              {deal.title}
            </h3>
          </Link>

          {/* Cupom se houver */}
          {deal.coupon_code && (
            <div className="mb-2">
              <button
                onClick={handleCopyCoupon}
                className="w-full flex items-center justify-between px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold hover:bg-emerald-500/20 transition-colors"
              >
                <span className="flex items-center gap-1 truncate">
                  <Ticket className="w-3 h-3 flex-shrink-0" /> Cupom: {deal.coupon_code}
                </span>
                <span className="text-[10px] uppercase font-bold flex-shrink-0">
                  {copiedCoupon ? "Copiado!" : "Copiar"}
                </span>
              </button>
            </div>
          )}

          {/* Preço Anterior / Queda */}
          <div className="h-5 mb-0.5 flex items-center text-xs">
            {deal.previous_price && deal.previous_price > deal.price ? (
              <span className="text-gray-400">
                De <span className="line-through">{formatBRL(deal.previous_price)}</span>
                <span className="text-rose-400 font-medium ml-1.5">↓ Caiu</span>
              </span>
            ) : deal.list_price && deal.list_price > deal.price ? (
              <span className="text-gray-400 line-through">
                De {formatBRL(deal.list_price)}
              </span>
            ) : (
              <span className="text-[11px] text-gray-500">Menor preço apurado</span>
            )}
          </div>

          {/* Preço Atual */}
          <div className="flex items-baseline gap-1.5 mb-2">
            <span className="text-xl font-black text-white tracking-tight">
              {formatBRL(deal.price)}
            </span>
            <span className="text-[11px] text-gray-400">à vista</span>
            {deal.free_shipping === 1 && (
              <span className="text-[10px] font-semibold text-emerald-400 ml-auto bg-emerald-500/10 px-1.5 py-0.5 rounded">
                Frete Grátis
              </span>
            )}
          </div>
        </div>

        {/* Ação Principal: Botão Limpo e Alto Impacto */}
        <div className="mt-3 pt-2.5 border-t border-white/[0.06] space-y-1.5">
          <a
            href={`${API_BASE}/r/${deal.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full text-xs font-bold text-white bg-rose-600 hover:bg-rose-500 py-2.5 rounded-xl flex items-center justify-center gap-1.5 transition-all shadow-sm"
          >
            Ver na Loja <ExternalLink className="w-3.5 h-3.5" />
          </a>
          <Link
            href={`/produto/${deal.id}`}
            className="block text-center text-[11px] text-gray-400 hover:text-gray-200 transition-colors py-0.5"
          >
            Ver histórico de preços →
          </Link>
        </div>
      </div>
    </div>
  );
}
