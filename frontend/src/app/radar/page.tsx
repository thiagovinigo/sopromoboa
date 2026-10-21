"use client";

import React, { useState, useEffect } from "react";
import { Flame, TrendingDown, Sparkles, Zap, ShieldCheck } from "lucide-react";
import DealCard from "@/components/DealCard";
import AlertModal from "@/components/AlertModal";
import { fetchRadarDeals, Deal } from "@/lib/api";
import { fetchFavoriteIds } from "@/lib/favorites";

export default function RadarPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [favoriteIds, setFavoriteIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDealForAlert, setSelectedDealForAlert] = useState<Deal | null>(null);
  const [isAlertOpen, setIsAlertOpen] = useState(false);

  useEffect(() => {
    fetchRadarDeals().then((res) => {
      setDeals(res);
      setLoading(false);
    });
    fetchFavoriteIds().then(setFavoriteIds);
  }, []);

  return (
    <div className="space-y-8">
      {/* Header do Radar */}
      <div className="relative overflow-hidden rounded-3xl p-8 border border-rose-500/30 bg-gradient-to-r from-rose-950/40 via-gray-900/80 to-gray-900/90 shadow-2xl">
        <div className="max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-black uppercase tracking-wider">
            <Flame className="w-4 h-4 fill-rose-500 text-rose-500 animate-pulse" />
            Radar de Quedas Recentes
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Itens Que Baixaram de Preço <br />
            <span className="text-rose-500">Nas Últimas 24h a 7 Dias</span>
          </h1>
          <p className="text-sm text-gray-300">
            Nossos workers comparam cada preço contra o histórico armazenado. Esta lista exibe apenas produtos com reduções reais de preço superiores a 2% e livres de falsas oscilações.
          </p>
        </div>
      </div>

      {/* Grade de Ofertas do Radar */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-rose-500" />
            Ofertas com Queda Comprovada
            <span className="text-xs font-normal text-gray-400">({deals.length} itens no radar)</span>
          </h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="glass-card rounded-2xl h-80 animate-pulse bg-gray-800/40" />
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="glass-card rounded-3xl p-12 text-center space-y-3">
            <ShieldCheck className="w-12 h-12 text-rose-400 mx-auto" />
            <h3 className="font-bold text-white text-lg">Nenhuma queda brusca detectada no momento</h3>
            <p className="text-xs text-gray-400 max-w-sm mx-auto">
              Novas reduções de preço serão adicionadas automaticamente assim que os scrapers detectarem rebaixamento nos e-commerces.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {deals.map((deal) => (
              <DealCard
                key={deal.id}
                deal={deal}
                isFavorited={favoriteIds.includes(deal.id)}
                onFavoriteChange={(id, isFav) => {
                  setFavoriteIds((prev) =>
                    isFav ? [...prev, id] : prev.filter((x) => x !== id)
                  );
                }}
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
