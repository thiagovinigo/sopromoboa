"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ExternalLink,
  Flame,
  TrendingDown,
  Star,
  Zap,
  Ticket,
  Bot,
  Check,
  ShieldCheck,
  ChevronLeft,
  Store,
  Sparkles,
} from "lucide-react";
import { fetchDealDetail, DealDetail, Deal } from "@/lib/api";
import PriceChart from "@/components/PriceChart";
import DealCard from "@/components/DealCard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function ProductDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [deal, setDeal] = useState<DealDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [copiedCoupon, setCopiedCoupon] = useState(false);
  const [isAlertOpen, setIsAlertOpen] = useState(false);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    if (id) {
      fetchDealDetail(id).then((res) => {
        setDeal(res);
        setLoading(false);
      });
    }
  }, [id]);

  const handleCopyCoupon = () => {
    if (deal?.coupon_code) {
      navigator.clipboard.writeText(deal.coupon_code);
      setCopiedCoupon(true);
      setTimeout(() => setCopiedCoupon(false), 2000);
    }
  };

  const formatBRL = (val: number) => {
    return val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-gray-800 rounded-xl w-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="glass-card h-96 rounded-3xl" />
          <div className="space-y-4">
            <div className="h-8 bg-gray-800 rounded-xl w-3/4" />
            <div className="h-12 bg-gray-800 rounded-xl w-1/2" />
            <div className="h-24 bg-gray-800 rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  if (!deal) {
    return (
      <div className="glass-card rounded-3xl p-12 text-center space-y-4">
        <Flame className="w-12 h-12 text-rose-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Oferta não encontrada ou esgotada</h2>
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gray-800 text-gray-300 hover:text-white text-xs font-semibold"
        >
          <ChevronLeft className="w-4 h-4" /> Voltar para a página inicial
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Breadcrumb de navegação */}
      <div className="flex items-center gap-2 text-xs text-gray-400">
        <Link href="/" className="hover:text-white transition-colors flex items-center gap-1">
          <ChevronLeft className="w-4 h-4" /> Voltar às ofertas
        </Link>
        <span>/</span>
        <span className="text-gray-300 uppercase font-semibold">{deal.category}</span>
        <span>/</span>
        <span className="text-gray-400 truncate max-w-xs">{deal.title}</span>
      </div>

      {/* Painel Principal do Produto */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        {/* Coluna da Imagem */}
        <div className="relative bg-gray-900/60 rounded-2xl overflow-hidden border border-gray-800/80 p-6 flex items-center justify-center min-h-[320px]">
          {deal.discount_percent > 0 && (
            <div className="absolute top-4 left-4 z-10 px-3 py-1.5 rounded-xl flame-gradient text-white text-xs font-black shadow-lg shadow-rose-600/30 flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 fill-white" />
              -{deal.discount_percent}% OFF
            </div>
          )}
          {deal.is_all_time_low && (
            <div className="absolute top-4 right-4 z-10 px-2.5 py-1 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-black uppercase tracking-wider flex items-center gap-1">
              <Flame className="w-3.5 h-3.5 text-emerald-400 fill-emerald-400" />
              Menor Preço
            </div>
          )}

          {deal.image_url && !imgError ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={deal.image_url}
              alt=""
              aria-label={deal.title}
              onError={() => setImgError(true)}
              className="max-h-80 w-auto object-contain hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="flex flex-col items-center justify-center p-8 text-center select-none">
              <div className="w-16 h-16 rounded-2xl bg-gray-800/80 border border-gray-700/60 flex items-center justify-center mb-2 shadow-inner">
                <Store className="w-8 h-8 text-rose-500" />
              </div>
              <span className="text-xs font-bold text-gray-300 uppercase tracking-wider">{deal.source}</span>
              <span className="text-xs text-gray-400 mt-1">{deal.brand || "Que Promo"}</span>
            </div>
          )}
        </div>

        {/* Coluna de Preços & Detalhes */}
        <div className="space-y-5">
          {/* Badges de Marca & Loja */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold flex items-center gap-1">
              <Store className="w-3.5 h-3.5" />
              {deal.source}
            </span>
            {deal.brand && (
              <span className="px-2.5 py-1 rounded-lg bg-gray-800 border border-gray-700 text-gray-300 text-xs font-semibold">
                Marca: {deal.brand}
              </span>
            )}
            {deal.rating && (
              <span className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold flex items-center gap-1">
                <Star className="w-3.5 h-3.5 fill-amber-400" />
                {deal.rating} {deal.review_count > 0 && `(${deal.review_count} avaliações)`}
              </span>
            )}
          </div>

          {/* Título Principal */}
          <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight leading-snug">
            {deal.title}
          </h1>

          {/* Card de Economia / Queda de Preço */}
          {deal.previous_price && deal.previous_price > deal.price && (
            <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flame-gradient flex items-center justify-center text-white flex-shrink-0">
                <TrendingDown className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs text-rose-300 font-bold block">
                  Queda de Preço Registrada pelo Radar!
                </span>
                <span className="text-xs text-gray-300">
                  Caiu de <span className="line-through">{formatBRL(deal.previous_price)}</span> para{" "}
                  <strong className="text-white font-bold">{formatBRL(deal.price)}</strong> (Você economiza {formatBRL(deal.previous_price - deal.price)})
                </span>
              </div>
            </div>
          )}

          {/* Seção de Preço */}
          <div className="space-y-1">
            {deal.list_price && deal.list_price > deal.price && (
              <div className="text-sm text-gray-400 line-through">
                De: {formatBRL(deal.list_price)}
              </div>
            )}
            <div className="flex items-baseline gap-3">
              <span className="text-3xl sm:text-4xl font-black text-white tracking-tight">
                {formatBRL(deal.price)}
              </span>
              <span className="text-xs text-gray-400 font-medium">
                à vista no Pix / Boleto
              </span>
            </div>
          </div>

          {/* Cupom se disponível */}
          {deal.coupon_code && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-dashed border-emerald-500/40 flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
                <Ticket className="w-4 h-4" />
                <span>Cupom de Desconto: <strong>{deal.coupon_code}</strong></span>
              </div>
              <button
                onClick={handleCopyCoupon}
                className="px-3 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-xs font-bold transition-colors"
              >
                {copiedCoupon ? "Copiado!" : "Copiar Cupom"}
              </button>
            </div>
          )}

          {deal.free_shipping === 1 && (
            <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
              <Check className="w-4 h-4" /> Frete Grátis disponível para este anúncio
            </div>
          )}

          {/* Botões de Conversão */}
          <div className="space-y-3 pt-2">
            <a
              href={`${API_BASE}/r/${deal.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-rose-600 via-rose-500 to-amber-500 hover:from-rose-500 hover:to-amber-400 text-white font-black text-base flex items-center justify-center gap-2 shadow-xl shadow-rose-600/30 transition-all hover:scale-[1.01]"
            >
              Ir Para a Loja com Desconto ({deal.source}) <ExternalLink className="w-5 h-5" />
            </a>

            <Link
              href={`/busca-personalizada?q=${encodeURIComponent(deal.title)}`}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-600/20 via-blue-600/20 to-indigo-600/20 hover:from-cyan-600/30 hover:to-indigo-600/30 text-cyan-300 hover:text-cyan-200 text-xs font-bold flex items-center justify-center gap-2 border border-cyan-500/40 transition-all shadow-lg shadow-cyan-950/40"
            >
              <Bot className="w-4 h-4 text-cyan-400" />
              Comparar Preços em Todas as Lojas (Workers)
            </Link>
          </div>
        </div>
      </div>

      {/* Gráfico de Evolução Histórica de Preço */}
      <section>
        <PriceChart
          history={deal.price_history}
          currentPrice={deal.price}
          lowestPrice={deal.lowest_historic_price}
        />
      </section>

      {/* Ofertas Semelhantes */}
      {deal.similar_deals && deal.similar_deals.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-rose-500" />
            Ofertas Similares em {deal.category.toUpperCase()}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
            {deal.similar_deals.map((s) => (
              <DealCard key={s.id} deal={s} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
