"use client";

import React, { useState, useEffect, useCallback } from "react";
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
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl p-8 sm:p-12 border border-gray-800 bg-gradient-to-b from-rose-950/20 via-gray-900/40 to-gray-900/80 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-rose-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl mx-auto text-center space-y-4 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold uppercase tracking-wider">
            <Flame className="w-3.5 h-3.5 fill-rose-500 text-rose-500" />
            Promoções com Quedas Reais de Preço
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            Chega de 'Metade do Dobro'. <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-400 via-rose-500 to-amber-400">
              Economia Real Comprovada.
            </span>
          </h1>

          <p className="text-gray-300 text-sm sm:text-base max-w-xl mx-auto">
            Varremos continuamente grandes lojas como Amazon, Mercado Livre e Magazine Luiza para catalogar quedas de preço legítimas e avisar você.
          </p>

          {/* Barra de Busca com Botão */}
          <form onSubmit={handleSearchSubmit} className="pt-2 max-w-2xl mx-auto">
            <div className="relative flex items-center shadow-2xl rounded-2xl bg-gray-900/90 border border-gray-700 focus-within:border-rose-500 transition-colors p-1.5">
              <Search className="w-5 h-5 text-gray-400 ml-3" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Busque por produto, marca ou modelo (ex: iPhone, Monitor, Air Fryer)..."
                className="w-full bg-transparent px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none"
              />
              <button
                type="submit"
                className="px-6 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-600 shadow-md shadow-rose-600/30 transition-all flex items-center gap-1.5"
              >
                Buscar
              </button>
            </div>
          </form>

          {/* Badges de Garantia */}
          <div className="flex flex-wrap items-center justify-center gap-6 pt-4 text-xs text-gray-400">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> Histórico de Preços Auditado
            </span>
            <span className="flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-amber-400" /> Detecção de Quedas Recentes
            </span>
            <span className="flex items-center gap-1.5">
              <Store className="w-4 h-4 text-blue-400" /> Lojas Oficiais & Verificadas
            </span>
          </div>
        </div>
      </section>

      {/* Barra de Filtros & Categorias */}
      <section className="space-y-4">
        {/* Categorias Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <button
            onClick={() => {
              setActiveCategory("");
              setPage(0);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
              activeCategory === ""
                ? "bg-rose-600 text-white shadow-lg shadow-rose-600/20"
                : "bg-gray-800/80 text-gray-300 hover:bg-gray-700/80"
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
              className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                activeCategory === c.slug
                  ? "bg-rose-600 text-white shadow-lg shadow-rose-600/20"
                  : "bg-gray-800/80 text-gray-300 hover:bg-gray-700/80"
              }`}
            >
              {c.name}
              {c.total_deals > 0 && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-black/40 text-gray-300">
                  {c.total_deals}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Lojas & Filtros de Ordenação */}
        <div className="flex flex-wrap items-center justify-between gap-4 bg-gray-900/60 p-3.5 rounded-2xl border border-gray-800">
          {/* Lojas Chips */}
          <div className="flex items-center gap-2 overflow-x-auto">
            <span className="text-xs font-semibold text-gray-400 flex items-center gap-1">
              <Store className="w-3.5 h-3.5" /> Lojas:
            </span>
            <button
              onClick={() => {
                setActiveStore("");
                setPage(0);
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                activeStore === "" ? "bg-gray-700 text-white" : "text-gray-400 hover:text-white"
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
                    ? "bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {s.name}
              </button>
            ))}
          </div>

          {/* Filtros Rápidos: Quedas & Ordenação */}
          <div className="flex items-center gap-3">
            {/* Toggle de Apenas Quedas */}
            <button
              onClick={() => {
                setOnlyDrops(!onlyDrops);
                setPage(0);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 border transition-all ${
                onlyDrops
                  ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                  : "bg-gray-800/80 text-gray-400 border-gray-700 hover:text-white"
              }`}
            >
              <TrendingDown className={`w-3.5 h-3.5 ${onlyDrops ? "text-rose-400" : ""}`} />
              Quedas Recentes
            </button>

            {/* Select de Ordenação */}
            <div className="flex items-center gap-1 text-xs">
              <SlidersHorizontal className="w-3.5 h-3.5 text-gray-400" />
              <select
                value={sort}
                onChange={(e) => {
                  setSort(e.target.value);
                  setPage(0);
                }}
                className="bg-gray-800 border border-gray-700 text-white text-xs font-semibold rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-rose-500"
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
