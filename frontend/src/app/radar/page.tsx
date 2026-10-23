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
      {/* Header do Radar - Limpo e Direto */}
      <div className="relative overflow-hidden rounded-3xl p-6 sm:p-8 border border-white/[0.07] bg-[#0d131f] shadow-lg">
        <div className="max-w-2xl space-y-2.5">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold">
            <Flame className="w-3.5 h-3.5 fill-rose-500 text-rose-500" />
            Radar de Quedas Recentes
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Produtos que baixaram de preço <span className="text-rose-500">recentemente</span>
          </h1>
          <p className="text-xs sm:text-sm text-gray-400">
            Comparamos cada valor contra o histórico apurado. Esta lista exibe apenas produtos com reduções legítimas nas últimas 24h a 7 dias.
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
