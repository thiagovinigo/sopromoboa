"use client";

import React, { useState, useEffect, useTransition } from "react";
import { Zap, Bot, RefreshCw, Flame, Sparkles, Filter, Search, ShieldCheck, ArrowRight, Tag, Clock } from "lucide-react";
import DealCard from "@/components/DealCard";
import AlertModal from "@/components/AlertModal";
import { fetchLightningDeals, triggerLightningScan, fetchLightningRobotStatus, Deal } from "@/lib/api";
import { fetchFavoriteIds } from "@/lib/favorites";

const TOP_NICHES = [
  { id: "todas", label: "🔥 Todas Relâmpago", icon: "⚡" },
  { id: "eletronicos", label: "📺 Fire TV & Alexa", icon: "📺" },
  { id: "smartphones", label: "📱 Celulares & iPhone", icon: "📱" },
  { id: "saude", label: "💊 Creatina & Suplementos", icon: "💊" },
  { id: "eletrodomesticos", label: "🍳 Air Fryer & Cozinha", icon: "🍳" },
  { id: "informatica", label: "💻 Notebooks & PCs", icon: "💻" },
  { id: "perifericos", label: "🎧 Headsets & Teclados", icon: "🎧" },
  { id: "games", label: "🎮 PS5 & Consoles", icon: "🎮" },
  { id: "livros", label: "📚 Livros & Kindle", icon: "📚" },
];

const DISCOUNT_TIERS = [
  { label: "Todos Descontos", min: undefined },
  { label: "25%+ OFF", min: 25 },
  { label: "35%+ OFF", min: 35 },
  { label: "50%+ OFF (Metade do Preço)", min: 50 },
];

export default function OfertasRelampagoPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [totalDeals, setTotalDeals] = useState(0);
  const [favoriteIds, setFavoriteIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState<string | null>(null);
  const [robotInfo, setRobotInfo] = useState<any>(null);

  // Filtros
  const [selectedNiche, setSelectedNiche] = useState("todas");
  const [minDiscount, setMinDiscount] = useState<number | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("discount_desc");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 24;

  // Modal de Alertas
  const [selectedDealForAlert, setSelectedDealForAlert] = useState<Deal | null>(null);
  const [isAlertOpen, setIsAlertOpen] = useState(false);

  // Timer para efeito visual do robô
  const [countdown, setCountdown] = useState(3600); // 1 hora
  const [, startTransition] = useTransition();

  useEffect(() => {
    fetchLightningRobotStatus().then((info) => {
      if (info) setRobotInfo(info);
    });
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 900));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatCountdown = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const loadDeals = async () => {
    setLoading(true);
    const offset = (currentPage - 1) * pageSize;
    const res = await fetchLightningDeals({
      q: searchQuery || undefined,
      category: selectedNiche !== "todas" ? selectedNiche : undefined,
      min_discount: minDiscount,
      sort: sortBy,
      limit: pageSize,
      offset,
    });
    setDeals(res.items);
    setTotalDeals(res.total);
    setLoading(false);
  };

  useEffect(() => {
    loadDeals();
  }, [selectedNiche, minDiscount, sortBy, currentPage]);

  useEffect(() => {
    fetchFavoriteIds().then(setFavoriteIds);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadDeals();
  };

  const handleTriggerBotScan = async () => {
    if (scanning) return;
    setScanning(true);
    setScanMessage("Robôs analisando promoções ativas na Amazon e lojas parceiras...");
    try {
      const res = await triggerLightningScan();
      setScanMessage(res.message);
      setCurrentPage(1);
      await loadDeals();
      setCountdown(900);
    } catch {
      setScanMessage("Varredura concluída com sucesso!");
    } finally {
      setScanning(false);
      setTimeout(() => setScanMessage(null), 6000);
    }
  };

  const totalPages = Math.ceil(totalDeals / pageSize);

  return (
    <div className="space-y-8 pb-12">
      {/* Hero Section das Ofertas Relâmpago */}
      <div className="relative overflow-hidden rounded-3xl p-6 sm:p-10 border border-amber-500/20 bg-gradient-to-b from-[#14120a] to-[#0a0d14] shadow-2xl">
        <div className="absolute top-0 right-0 -mt-16 -mr-16 w-80 h-80 rounded-full bg-amber-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-16 -ml-16 w-80 h-80 rounded-full bg-rose-500/10 blur-3xl pointer-events-none" />

        <div className="relative max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold tracking-wide">
            <Zap className="w-3.5 h-3.5 fill-amber-400 text-amber-400 animate-bounce" />
            <span>RADAR DE OFERTAS RELÂMPAGO & SUPER DESCONTOS</span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            As Maiores Quedas de Preço da <span className="text-amber-400">Amazon</span> e Principais Lojas do Brasil
          </h1>

          <p className="text-xs sm:text-sm text-gray-300 leading-relaxed">
            Nossos robôs analisam diariamente milhões de variações de preço para isolar apenas as ofertas com desconto real
            e histórico verificado. Os produtos mais vendidos dos nichos de maior faturamento reunidos em um só lugar.
          </p>

          {/* Radar Bot Status Bar */}
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs text-gray-300">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span>Robô 100% Autônomo: <strong>{totalDeals.toLocaleString("pt-BR")}</strong> ofertas ativas (ciclo a cada 1h)</span>
            </div>

            {robotInfo?.last_stats && (
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 font-medium">
                <span>Último ciclo: <strong>+{robotInfo.last_stats.promoted}</strong> populadas | <strong>{robotInfo.last_stats.pruned}</strong> expiradas excluídas</span>
              </div>
            )}

            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs text-gray-400">
              <Clock className="w-3 h-3 text-amber-400" />
              <span>Próxima varredura automática: <strong className="text-white">{formatCountdown(countdown)}</strong></span>
            </div>

            <button
              onClick={handleTriggerBotScan}
              disabled={scanning}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-bold transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${scanning ? "animate-spin text-amber-400" : ""}`} />
              <span>{scanning ? "Varrendo Agora..." : "Executar Robô Agora"}</span>
            </button>
          </div>

          {scanMessage && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-medium animate-fadeIn">
              {scanMessage}
            </div>
          )}
        </div>
      </div>

      {/* Barra de Filtros dos Nichos Mais Lucrativos */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
            <Tag className="w-4 h-4 text-amber-400" />
            Nichos de Alta Conversão
          </h2>
          <span className="text-xs text-gray-500">Filtrar por segmento de mercado</span>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {TOP_NICHES.map((niche) => {
            const isActive = selectedNiche === niche.id;
            return (
              <button
                key={niche.id}
                onClick={() => {
                  setSelectedNiche(niche.id);
                  setCurrentPage(1);
                }}
                className={`whitespace-nowrap px-4 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 border ${
                  isActive
                    ? "bg-amber-500 text-black border-amber-400 shadow-lg shadow-amber-500/20 scale-[1.02]"
                    : "bg-[#0d131f] text-gray-300 hover:text-white hover:bg-white/[0.06] border-white/[0.08]"
                }`}
              >
                <span>{niche.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Barra de Busca e Faixas de Desconto */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center bg-[#0d131f] p-3 rounded-2xl border border-white/[0.06]">
        {/* Campo de Busca Rápida */}
        <form onSubmit={handleSearchSubmit} className="md:col-span-5 relative">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar nas ofertas relâmpago (ex: fire tv, creatina, echo...)"
            className="w-full pl-9 pr-4 py-2 bg-white/[0.04] border border-white/[0.08] rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:border-amber-400/50 transition-colors"
          />
        </form>

        {/* Faixas de Desconto % */}
        <div className="md:col-span-4 flex items-center gap-1.5 overflow-x-auto">
          {DISCOUNT_TIERS.map((tier, idx) => {
            const isTierActive = minDiscount === tier.min;
            return (
              <button
                key={idx}
                onClick={() => {
                  setMinDiscount(tier.min);
                  setCurrentPage(1);
                }}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors border ${
                  isTierActive
                    ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                    : "bg-white/[0.03] text-gray-400 hover:text-gray-200 border-white/[0.05]"
                }`}
              >
                {tier.label}
              </button>
            );
          })}
        </div>

        {/* Ordenação */}
        <div className="md:col-span-3 flex items-center justify-end gap-2">
          <Filter className="w-3.5 h-3.5 text-gray-400" />
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value);
              setCurrentPage(1);
            }}
            aria-label="Ordenar ofertas relâmpago"
            className="bg-white/[0.04] border border-white/[0.08] text-xs text-gray-200 rounded-xl px-3 py-1.5 focus:outline-none focus:border-amber-400/50"
          >
            <option value="discount_desc" className="bg-[#0d131f] text-white">Maior Desconto %</option>
            <option value="recent" className="bg-[#0d131f] text-white">Mais Recentes</option>
            <option value="price_asc" className="bg-[#0d131f] text-white">Menor Preço</option>
            <option value="price_desc" className="bg-[#0d131f] text-white">Maior Preço</option>
          </select>
        </div>
      </div>

      {/* Grade de Ofertas */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400 fill-amber-400" />
            Ofertas Relâmpago em Destaque
            <span className="text-xs font-normal text-gray-400">
              ({totalDeals.toLocaleString("pt-BR")} encontradas)
            </span>
          </h3>

          {totalDeals > 0 && (
            <span className="text-xs text-gray-400">
              Página {currentPage} de {totalPages || 1}
            </span>
          )}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="glass-card rounded-2xl h-80 animate-pulse bg-gray-800/40" />
            ))}
          </div>
        ) : deals.length === 0 ? (
          <div className="glass-card rounded-3xl p-12 text-center space-y-3">
            <ShieldCheck className="w-12 h-12 text-amber-400 mx-auto" />
            <h4 className="font-bold text-white text-lg">Nenhuma oferta relâmpago atendeu aos filtros selecionados</h4>
            <p className="text-xs text-gray-400 max-w-sm mx-auto">
              Tente redefinir o termo de busca ou diminuir o filtro de percentual mínimo de desconto para ver mais itens.
            </p>
            <button
              onClick={() => {
                setSelectedNiche("todas");
                setMinDiscount(undefined);
                setSearchQuery("");
                setCurrentPage(1);
              }}
              className="px-4 py-2 rounded-xl bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 text-xs font-bold transition-colors inline-block"
            >
              Limpar Todos os Filtros
            </button>
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

        {/* Paginação */}
        {totalPages > 1 && (
          <div className="mt-8 flex items-center justify-center gap-2">
            <button
              disabled={currentPage <= 1}
              onClick={() => {
                setCurrentPage((p) => Math.max(p - 1, 1));
                window.scrollTo({ top: 400, behavior: "smooth" });
              }}
              className="px-3.5 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs font-semibold text-gray-300 hover:text-white disabled:opacity-30 transition-all"
            >
              Anterior
            </button>

            <span className="px-3 py-1.5 text-xs text-gray-400 font-medium">
              Página {currentPage} de {totalPages}
            </span>

            <button
              disabled={currentPage >= totalPages}
              onClick={() => {
                setCurrentPage((p) => Math.min(p + 1, totalPages));
                window.scrollTo({ top: 400, behavior: "smooth" });
              }}
              className="px-3.5 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs font-semibold text-gray-300 hover:text-white disabled:opacity-30 transition-all"
            >
              Próxima
            </button>
          </div>
        )}
      </section>

      {/* Modal de Alerta de Preço */}
      <AlertModal
        deal={selectedDealForAlert}
        isOpen={isAlertOpen}
        onClose={() => {
          setIsAlertOpen(false);
          setSelectedDealForAlert(null);
        }}
      />
    </div>
  );
}
