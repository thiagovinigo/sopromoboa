"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Search,
  Flame,
  SlidersHorizontal,
  TrendingDown,
  Sparkles,
  Store,
  Layers,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Zap,
} from "lucide-react";
import DealCard from "@/components/DealCard";
import {
  fetchDeals,
  fetchCategories,
  fetchStores,
  Deal,
  CategoryItem,
  StoreItem,
} from "@/lib/api";
import { fetchFavoriteIds } from "@/lib/favorites";

export default function HomePage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [favoriteIds, setFavoriteIds] = useState<string[]>([]);

  // Filtros
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("");
  const [activeStore, setActiveStore] = useState<string>("");
  const [onlyDrops, setOnlyDrops] = useState<boolean>(false);
  const [sort, setSort] = useState<string>("recent");
  const [page, setPage] = useState(0);
  const pageSize = 20;

  // Categorias e Lojas
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [stores, setStores] = useState<StoreItem[]>([]);

  // Carrega categorias, lojas e favoritos iniciais
  useEffect(() => {
    fetchCategories().then(setCategories);
    fetchStores().then(setStores);
    fetchFavoriteIds().then(setFavoriteIds);

    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const storeParam = params.get("source") || params.get("loja");
      if (storeParam) {
        setActiveStore(storeParam);
      }
      const catParam = params.get("category");
      if (catParam) {
        setActiveCategory(catParam);
      }
    }
  }, []);

  const loadDeals = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchDeals({
        q: search.trim() || undefined,
        category: activeCategory || undefined,
        source: activeStore || undefined,
        only_drops: onlyDrops,
        sort: sort,
        limit: pageSize,
        offset: page * pageSize,
      });
      setDeals(res.items);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  }, [search, activeCategory, activeStore, onlyDrops, sort, page]);

  useEffect(() => {
    loadDeals();
  }, [loadDeals]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    loadDeals();
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      {/* Hero Section - Clean & Breathable */}
      <section className="relative overflow-hidden rounded-3xl p-6 sm:p-10 border border-white/[0.07] bg-[#0d131f] shadow-lg">
        <div className="max-w-2xl mx-auto text-center space-y-3.5 relative z-10">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold">
            <Flame className="w-3.5 h-3.5 fill-rose-500 text-rose-500" />
            Radar de Quedas de Preço & Ofertas Reais
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Economia real, <span className="text-rose-500">sem pegadinhas</span>.
          </h1>

          <p className="text-gray-400 text-xs sm:text-sm max-w-lg mx-auto leading-relaxed">
            Varremos continuamente grandes lojas como Amazon, Mercado Livre e Magalu para alertar apenas quedas de preço comprovadas.
          </p>

          {/* Barra de Busca Flutuante e Limpa */}
          <form onSubmit={handleSearchSubmit} className="pt-2 max-w-xl mx-auto">
            <div className="relative flex items-center bg-[#080c14] border border-white/10 rounded-2xl p-1.5 shadow-inner focus-within:border-rose-500/60 transition-colors">
              <Search className="w-4 h-4 text-gray-400 ml-3 flex-shrink-0" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Busque por iPhone, Monitor, TV, Notebook..."
                className="w-full bg-transparent px-3 py-2 text-xs sm:text-sm text-white placeholder-gray-500 focus:outline-none"
              />
              <button
                type="submit"
                className="px-5 py-2 rounded-xl font-bold text-xs text-white bg-rose-600 hover:bg-rose-500 transition-colors flex-shrink-0 shadow-sm"
              >
                Buscar
              </button>
            </div>
          </form>

          {/* Badges de Confiança */}
          <div className="flex flex-wrap items-center justify-center gap-5 pt-2 text-[11px] text-gray-400">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Histórico auditado
            </span>
            <span className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Quedas em tempo real
            </span>
            <span className="flex items-center gap-1.5">
              <Store className="w-3.5 h-3.5 text-blue-400" /> Lojas oficiais
            </span>
          </div>
        </div>
      </section>

      {/* Banner de Destaque das Ofertas Relâmpago & Nichos que Mais Faturam */}
      <Link
        href="/ofertas-relampago"
        className="block group relative overflow-hidden rounded-3xl p-5 sm:p-6 border border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-[#0d131f] to-rose-500/10 hover:border-amber-500/50 transition-all shadow-lg hover:shadow-amber-500/10"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-300 shrink-0 group-hover:scale-105 transition-transform shadow-md shadow-amber-500/20">
              <Zap className="w-6 h-6 fill-amber-400 text-amber-400 animate-pulse" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-extrabold text-base text-white group-hover:text-amber-300 transition-colors">
                  ⚡ Central de Ofertas Relâmpago & Super Descontos
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-500 text-black uppercase tracking-wider">
                  3.800+ Ofertas Auditadas
                </span>
              </div>
              <p className="text-xs text-gray-300 mt-0.5">
                Fire TV Stick, Alexa Echo, Creatina Creapure, Air Fryer, iPhone 15 e os nichos mais vendidos com <strong>25% a 70% OFF</strong>.
              </p>
            </div>
          </div>

          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-black text-xs font-black shrink-0 self-start sm:self-center transition-all shadow-md shadow-amber-500/30 group-hover:scale-105">
            <span>Ver Ofertas Relâmpago</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      </Link>

      {/* Barra de Filtros & Categorias */}
      <section className="space-y-3">
        {/* Categorias Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          <button
            onClick={() => {
              setActiveCategory("");
              setPage(0);
            }}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
              activeCategory === ""
                ? "bg-rose-600 text-white shadow-sm"
                : "bg-white/[0.04] text-gray-300 hover:bg-white/[0.08] hover:text-white border border-white/[0.06]"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Todas as Categorias
          </button>
          {categories.map((c) => (
            <button
              key={c.slug}
              onClick={() => {
                setActiveCategory(c.slug);
                setPage(0);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                activeCategory === c.slug
                  ? "bg-rose-600 text-white shadow-sm"
                  : "bg-white/[0.04] text-gray-300 hover:bg-white/[0.08] hover:text-white border border-white/[0.06]"
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>

        {/* Lojas & Filtros Rápidos */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-[#0d131f] p-3 rounded-2xl border border-white/[0.06]">
          {/* Lojas Chips */}
          <div className="flex items-center gap-1.5 overflow-x-auto">
            <span className="text-xs font-medium text-gray-400 flex items-center gap-1 mr-1">
              <Store className="w-3.5 h-3.5" /> Lojas:
            </span>
            <button
              onClick={() => {
                setActiveStore("");
                setPage(0);
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                activeStore === "" ? "bg-white/[0.1] text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              Todas
            </button>
            {stores.map((s) => (
              <button
                key={s.slug}
                onClick={() => {
                  setActiveStore(s.name);
                  setPage(0);
                }}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                  activeStore.toLowerCase() === s.name.toLowerCase()
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {s.name}
              </button>
            ))}
          </div>

          {/* Filtros Rápidos: Quedas & Ordenação */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setOnlyDrops(!onlyDrops);
                setPage(0);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                onlyDrops
                  ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                  : "bg-white/[0.04] text-gray-400 border-white/[0.06] hover:text-white"
              }`}
            >
              <TrendingDown className={`w-3.5 h-3.5 ${onlyDrops ? "text-rose-400" : ""}`} />
              Quedas Recentes
            </button>

            <div className="flex items-center gap-1 text-xs">
              <SlidersHorizontal className="w-3.5 h-3.5 text-gray-400" />
              <select
                value={sort}
                onChange={(e) => {
                  setSort(e.target.value);
                  setPage(0);
                }}
                className="bg-[#080c14] border border-white/10 text-white text-xs font-medium rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-rose-500"
              >
                <option value="recent">Mais Recentes</option>
                <option value="drop_desc">Maior Queda de Preço</option>
                <option value="discount_desc">Maior % de Desconto</option>
                <option value="price_asc">Menor Preço</option>
                <option value="price_desc">Maior Preço</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      {/* Grade de Ofertas */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-rose-500" />
            Ofertas Encontradas
            <span className="text-xs font-normal text-gray-400">({total} promoções)</span>
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
            <Flame className="w-12 h-12 text-gray-600 mx-auto" />
            <h3 className="font-bold text-white text-lg">Nenhuma oferta encontrada</h3>
            <p className="text-xs text-gray-400 max-w-sm mx-auto">
              Tente ajustar os filtros, termo de busca ou aguarde a próxima varredura dos workers.
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
              />
            ))}
          </div>
        )}

        {/* Paginação */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-8">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-2 rounded-xl bg-gray-800 text-gray-300 hover:text-white disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-xs font-bold text-gray-300">
              Página {page + 1} de {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="p-2 rounded-xl bg-gray-800 text-gray-300 hover:text-white disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </section>
    </div>
  );
}
