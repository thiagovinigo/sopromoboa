"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Heart, Flame, Sparkles, TrendingDown, ArrowRight } from "lucide-react";
import DealCard from "@/components/DealCard";
import AlertModal from "@/components/AlertModal";
import { fetchFavorites } from "@/lib/favorites";
import { Deal } from "@/lib/api";

export default function FavoritesPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDealForAlert, setSelectedDealForAlert] = useState<Deal | null>(null);
  const [isAlertOpen, setIsAlertOpen] = useState(false);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = () => {
    fetchFavorites().then((res) => {
      setDeals(res);
      setLoading(false);
    });
  };

  const handleFavoriteChange = (dealId: string, isFav: boolean) => {
    if (!isFav) {
      setDeals((prev) => prev.filter((d) => d.id !== dealId));
    }
  };

  const dropsCount = deals.filter((d) => d.price_dropped === 1).length;

  return (
    <div className="space-y-8">
      {/* Header dos Favoritos */}
      <div className="relative overflow-hidden rounded-3xl p-8 border border-rose-500/30 bg-gradient-to-r from-rose-950/40 via-gray-900/80 to-gray-900/90 shadow-2xl">
        <div className="max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-black uppercase tracking-wider">
            <Heart className="w-4 h-4 fill-rose-500 text-rose-500" />
            Minha Lista de Desejos
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Produtos Favoritos & <br />
            <span className="text-rose-500">Monitoramento Pessoal</span>
          </h1>
          <p className="text-sm text-gray-300">
            Acompanhe a variação de preço dos produtos que você salvou. Se o preço cair, avisamos você imediatamente com o destaque no topo!
          </p>
        </div>
      </div>

      {/* Banner de Aviso de Queda de Preço nos Favoritos */}
      {dropsCount > 0 && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-rose-600/30 via-rose-500/20 to-amber-500/20 border border-rose-500/40 flex items-center justify-between gap-4 animate-fade-in shadow-xl shadow-rose-600/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flame-gradient flex items-center justify-center text-white flex-shrink-0 shadow-lg shadow-rose-600/30">
              <TrendingDown className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-white text-sm block">
                Oportunidade! {dropsCount} {dropsCount === 1 ? "produto favorito seu baixou" : "produtos favoritos seus baixaram"} de preço!
              </span>
              <span className="text-xs text-rose-300">
                Aproveite enquanto o estoque das lojas de origem estiver disponível.
              </span>
            </div>
          </div>
          <Link
            href="/radar"
            className="hidden sm:flex items-center gap-1 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition-all shadow-md"
          >
            Ver no Radar <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Grade de Itens Favoritados */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Heart className="w-5 h-5 text-rose-500 fill-rose-500" />
            Itens Salvos ({deals.length})
          </h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="glass-card rounded-2xl h-80 animate-pulse bg-gray-800/40" />
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="glass-card rounded-3xl p-12 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mx-auto">
              <Heart className="w-8 h-8" />
            </div>
            <h3 className="font-bold text-white text-lg">Sua lista de favoritos está vazia</h3>
            <p className="text-xs text-gray-400 max-w-sm mx-auto">
              Navegue pelas ofertas na vitrine ou pelo radar e clique no ícone de coração nos produtos que deseja monitorar.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-600 shadow-md shadow-rose-600/20 transition-all"
            >
              <Sparkles className="w-4 h-4" /> Explorar Ofertas Agora
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {deals.map((deal) => (
              <DealCard
                key={deal.id}
                deal={deal}
                isFavorited={true}
                onFavoriteChange={handleFavoriteChange}
                onOpenAlertModal={(d) => {
                  setSelectedDealForAlert(d);
                  setIsAlertOpen(true);
                }}
              />
            ))}
          </div>
        )}
      </section>

      {/* Modal de Alerta */}
      <AlertModal
        deal={selectedDealForAlert}
        isOpen={isAlertOpen}
        onClose={() => setIsAlertOpen(false)}
      />
    </div>
  );
}
