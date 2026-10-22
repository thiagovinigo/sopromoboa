"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ExternalLink,
  TrendingDown,
  Star,
  Zap,
  Ticket,
  Bell,
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
    <div className="glass-card rounded-2xl overflow-hidden flex flex-col transition-all duration-300 hover:-translate-y-1 group relative">
      {/* Badges superiores - isolados com pointer-events-none e limite de largura */}
      <div className="absolute top-2.5 left-2.5 z-20 flex flex-wrap gap-1.5 items-center pointer-events-none max-w-[70%]">
        {deal.discount_percent > 0 && (
          <span className="px-2 py-0.5 text-xs font-black text-white flame-gradient rounded-lg shadow-md shadow-rose-600/30 flex items-center gap-1">
            <Zap className="w-3 h-3 fill-white" />
            -{deal.discount_percent}%
          </span>
        )}
        {deal.is_all_time_low && (
          <span className="px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-emerald-300 bg-emerald-950/90 backdrop-blur-md border border-emerald-500/40 rounded-md flex items-center gap-1 shadow-sm">
            <Flame className="w-3 h-3 text-emerald-400 fill-emerald-400" />
            Menor Preço
          </span>
        )}
        {deal.is_affiliate_deal === 1 && (
          <span className="px-2 py-0.5 text-[10px] font-black uppercase tracking-wider text-purple-300 bg-purple-950/90 backdrop-blur-md border border-purple-500/40 rounded-md shadow-sm flex items-center gap-1">
            <Sparkles className="w-2.5 h-2.5 text-purple-400" /> Destaque
          </span>
        )}
      </div>

      {/* Ações superiores direitas: Favoritar e Alerta */}
      <div className="absolute top-2.5 right-2.5 z-20 flex items-center gap-1.5">
        <button
          onClick={handleToggleFavorite}
          title={isFav ? "Remover dos favoritos" : "Salvar nos favoritos"}
          className={`p-1.5 rounded-full backdrop-blur-md transition-all ${
            isFav
              ? "bg-rose-500 text-white shadow-lg shadow-rose-500/40 scale-105"
              : "bg-gray-900/80 text-gray-400 hover:text-rose-400 hover:bg-rose-500/20 border border-gray-700"
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

        <button
          onClick={() => onOpenAlertModal && onOpenAlertModal(deal)}
          title="Criar alerta de preço para este item"
          className="p-1.5 rounded-full bg-gray-900/80 hover:bg-amber-500/20 text-gray-400 hover:text-amber-400 border border-gray-700 hover:border-amber-500/40 transition-colors"
        >
          <Bell className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Imagem do Produto com Fallback Blindado (sem texto quebrado sobreposto) */}
      <Link
        href={`/produto/${deal.id}`}
        className="block relative pt-[72%] bg-gradient-to-b from-gray-900/90 to-gray-950/90 overflow-hidden"
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
          <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center select-none bg-gradient-to-b from-gray-900/95 to-gray-950">
            <div className="w-12 h-12 rounded-2xl bg-gray-800/80 border border-gray-700/60 flex items-center justify-center mb-1.5 shadow-inner group-hover:scale-110 transition-transform">
              <CategoryIconComponent className="w-6 h-6 text-rose-500" />
            </div>
            <span className="text-[11px] font-black tracking-wider text-gray-300 uppercase">{deal.source}</span>
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
            <span className={`px-2 py-0.5 rounded-md font-semibold border ${getStoreBadgeColor(deal.source)}`}>
              {deal.source}
            </span>
            {deal.rating ? (
              <span className="flex items-center gap-1 text-amber-400 font-semibold text-xs">
                <Star className="w-3 h-3 fill-amber-400" />
                {deal.rating} {deal.review_count > 0 && `(${deal.review_count})`}
              </span>
            ) : (
              <span className="text-[10px] text-gray-500 uppercase tracking-wider">{deal.category}</span>
            )}
          </div>

          {/* Título com altura fixa de 2 linhas para garantir alinhamento perfeito */}
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
                className="w-full flex items-center justify-between px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-dashed border-emerald-500/40 text-emerald-400 text-xs font-bold hover:bg-emerald-500/20 transition-colors"
              >
                <span className="flex items-center gap-1">
                  <Ticket className="w-3 h-3" /> Cupom: {deal.coupon_code}
                </span>
                <span className="text-[10px] uppercase font-semibold">
                  {copiedCoupon ? "Copiado!" : "Copiar"}
                </span>
              </button>
            </div>
          )}

          {/* Linha de Queda de Preço com altura fixa para evitar desníveis */}
          <div className="h-5 mb-1 flex items-center">
            {deal.previous_price && deal.previous_price > deal.price ? (
              <div className="flex items-center gap-1 text-xs text-rose-400 font-bold">
                <TrendingDown className="w-3.5 h-3.5" />
                <span>Caiu de <span className="line-through text-gray-400 font-normal">{formatBRL(deal.previous_price)}</span></span>
              </div>
            ) : deal.list_price && deal.list_price > deal.price ? (
              <div className="text-xs text-gray-400 line-through">
                De: {formatBRL(deal.list_price)}
              </div>
            ) : (
              <span className="text-[11px] text-gray-500">Preço verificado</span>
            )}
          </div>

          {/* Preço Atual */}
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-xl font-black text-white tracking-tight">
              {formatBRL(deal.price)}
            </span>
            <span className="text-[11px] text-gray-400">à vista / Pix</span>
          </div>

          {deal.free_shipping === 1 && (
            <div className="inline-block text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full mb-3">
              ✓ Frete Grátis
            </div>
          )}
        </div>

        {/* Botões de Ação */}
        <div className="grid grid-cols-2 gap-2 mt-auto pt-2 border-t border-gray-800/80">
          <Link
            href={`/produto/${deal.id}`}
            className="text-xs font-semibold text-gray-300 hover:text-white bg-gray-800/80 hover:bg-gray-700/80 py-2 rounded-xl text-center transition-colors"
          >
            Histórico
          </Link>
          <a
            href={`${API_BASE}/r/${deal.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-bold text-white bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-600 py-2 rounded-xl flex items-center justify-center gap-1 shadow-md shadow-rose-600/20 transition-all hover:scale-[1.02]"
          >
            Pegar <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
}
