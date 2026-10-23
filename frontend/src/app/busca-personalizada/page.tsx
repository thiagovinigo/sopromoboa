"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Search,
  Bot,
  Sparkles,
  TrendingDown,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Store,
  Layers,
  ArrowRight,
  Flame,
  Zap,
  ShoppingBag,
  RefreshCw,
  Award,
  DollarSign,
  Truck,
  SlidersHorizontal,
} from "lucide-react";
import {
  fetchComparatorSearch,
  WorkerSearchResult,
  StorePriceComparison,
  Deal,
} from "@/lib/api";
import DealCard from "@/components/DealCard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const POPULAR_SUGGESTIONS = [
  "iPhone 15",
  "PlayStation 5",
  "Air Fryer Mondial",
  "RTX 4060",
  "Samsung Galaxy S24",
  "Smart TV 55",
  "Echo Dot Alexa",
  "Monitor 27",
  "Fritadeira",
  "SSD 1TB",
];

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const initialQuery = searchParams?.get("q") || "";
  const [searchTerm, setSearchTerm] = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WorkerSearchResult | null>(null);
  const [workerStep, setWorkerStep] = useState(0);

  useEffect(() => {
    if (initialQuery) {
      setSearchTerm(initialQuery);
      setActiveQuery(initialQuery);
      executeSearch(initialQuery);
    }
  }, [initialQuery]);

  const executeSearch = async (queryText: string) => {
    const q = queryText.trim();
    if (!q) return;

    setLoading(true);
    setWorkerStep(1);

    const stepTimer1 = setTimeout(() => setWorkerStep(2), 600);
    const stepTimer2 = setTimeout(() => setWorkerStep(3), 1200);

    try {
      const data = await fetchComparatorSearch(q);
      setResult(data);
    } catch (err) {
      console.error("Erro na busca:", err);
    } finally {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setLoading(false);
      setWorkerStep(0);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      router.push(`/busca-personalizada?q=${encodeURIComponent(searchTerm.trim())}`);
      setActiveQuery(searchTerm.trim());
      executeSearch(searchTerm.trim());
    }
  };

  const handleSelectSuggestion = (suggestion: string) => {
    setSearchTerm(suggestion);
    router.push(`/busca-personalizada?q=${encodeURIComponent(suggestion)}`);
    setActiveQuery(suggestion);
    executeSearch(suggestion);
  };

  const formatBRL = (val?: number | null) => {
    if (val === undefined || val === null || val === 0) return "Consulte na loja";
    return val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  };

  return (
    <div className="space-y-8">
      {/* Hero: Cabeçalho da Busca Personalizada */}
      <section className="relative overflow-hidden rounded-3xl p-8 sm:p-12 border border-cyan-500/30 bg-gradient-to-b from-cyan-950/30 via-gray-900/60 to-gray-900/90 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl mx-auto text-center space-y-4 relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider shadow-lg shadow-cyan-950/50">
            <Bot className="w-4 h-4 text-cyan-400 animate-pulse" />
            Workers &amp; Robôs de Comparação Inteligente
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            Busca Personalizada <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400">
              Melhores Preços de Todos os Sites
            </span>
          </h1>

          <p className="text-gray-300 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
            Informe o produto que você quer comprar. Nossos robôs varrem continuamente a <strong>Amazon, Mercado Livre, Magazine Luiza, KaBuM! e Shopee</strong> para montar uma página exclusiva com o menor preço e comparativo loja a loja.
          </p>

          {/* Form de Busca */}
          <form onSubmit={handleSubmit} className="pt-3 max-w-2xl mx-auto">
            <div className="relative flex items-center shadow-2xl rounded-2xl bg-gray-900/95 border-2 border-cyan-500/40 focus-within:border-cyan-400 transition-all p-1.5">
              <Search className="w-5 h-5 text-cyan-400 ml-3 shrink-0" />
              <input
                type="text"
                placeholder="Ex: iPhone 15, PlayStation 5, Air Fryer Mondial, RTX 4060..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-transparent px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none"
              />
              <button
                type="submit"
                disabled={loading || !searchTerm.trim()}
                className="px-6 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 shadow-lg shadow-cyan-600/30 transition-all flex items-center gap-2 disabled:opacity-50 shrink-0"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Varrendo...
                  </>
                ) : (
                  <>
                    <Bot className="w-4 h-4" />
                    Customizar Página
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Chips de Sugestões Rápidas */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
            <span className="text-[11px] font-semibold text-gray-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-cyan-400" /> Populares:
            </span>
            {POPULAR_SUGGESTIONS.map((sug) => (
              <button
                key={sug}
                onClick={() => handleSelectSuggestion(sug)}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-800/80 hover:bg-cyan-950/50 text-gray-300 hover:text-cyan-300 border border-gray-700 hover:border-cyan-500/30 transition-all"
              >
                {sug}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Animação dos Workers em Execução */}
      {loading && (
        <div className="glass-card rounded-3xl p-8 border border-cyan-500/30 bg-gray-900/80 text-center space-y-5 animate-pulse">
          <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center mx-auto text-cyan-400 shadow-xl shadow-cyan-950">
            <Bot className="w-7 h-7 animate-bounce" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Nossos Workers estão customizando a sua página...</h3>
            <p className="text-xs text-gray-400 mt-1">Varrendo preços e calculando a melhor oferta em tempo real</p>
          </div>
          <div className="max-w-md mx-auto space-y-2 text-xs text-left bg-gray-950/60 p-4 rounded-xl border border-gray-800 font-mono">
            <div className="flex items-center gap-2 text-cyan-400">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Conectando aos scrapers de Amazon, Mercado Livre, Magalu e KaBuM!...</span>
            </div>
            {workerStep >= 2 && (
              <div className="flex items-center gap-2 text-teal-400">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Catalogando preços e identificando menor histórico...</span>
              </div>
            )}
            {workerStep >= 3 && (
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Aplicando links comissionados e gerando comparativo de economia!</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Resultados da Busca Customizada */}
      {!loading && result && (
        <div className="space-y-8 animate-fadeIn">
          {/* Header da Página Customizada */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-gray-900/90 via-gray-900/60 to-gray-950 border border-gray-800">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1">
                <Sparkles className="w-3.5 h-3.5" /> Página Customizada Gerada com Sucesso
              </div>
              <h2 className="text-2xl font-black text-white">
                Melhores Preços para: <span className="text-cyan-400">&ldquo;{result.query}&rdquo;</span>
              </h2>
              <p className="text-xs text-gray-400 mt-1">
                {result.total_found > 0
                  ? `Analisamos ${result.total_found} ofertas em ${result.stores_comparison.length} lojas parceiras.`
                  : `Nenhum anúncio direto no catálogo local, mas geramos os atalhos de busca oficiais das maiores lojas para você.`}
              </p>

              {result.did_you_mean && (
                <div className="mt-3 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-start sm:items-center gap-2.5 text-cyan-300 text-xs shadow-inner">
                  <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5 sm:mt-0" />
                  <span>
                    {result.did_you_mean_notice || (
                      <>Exibindo resultados customizados para: <strong>{result.did_you_mean}</strong></>
                    )}
                  </span>
                </div>
              )}
            </div>

            {result.best_store && (
              <div className="flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/30 px-4 py-2.5 rounded-xl text-emerald-400">
                <Award className="w-6 h-6 text-emerald-400 shrink-0" />
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-wider block text-emerald-500">Loja Mais Barata</span>
                  <span className="text-sm font-black text-white">{result.best_store}</span>
                </div>
              </div>
            )}
          </div>

          {/* Cards de Métricas e Economia Real */}
          {result.best_price && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass-card p-5 rounded-2xl border border-emerald-500/30 bg-gradient-to-b from-emerald-950/20 to-gray-900/80">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Award className="w-4 h-4" /> Melhor Preço
                </span>
                <div className="text-2xl font-black text-white mt-2">
                  {formatBRL(result.best_price)}
                </div>
                <span className="text-xs text-gray-400 mt-1 block">
                  Disponível na <strong>{result.best_store}</strong>
                </span>
              </div>

              {result.potential_savings && result.potential_savings > 0 && (
                <div className="glass-card p-5 rounded-2xl border border-cyan-500/30 bg-gradient-to-b from-cyan-950/20 to-gray-900/80">
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                    <TrendingDown className="w-4 h-4" /> Economia Máxima
                  </span>
                  <div className="text-2xl font-black text-cyan-300 mt-2">
                    {formatBRL(result.potential_savings)}
                  </div>
                  <span className="text-xs text-gray-400 mt-1 block">
                    Diferença entre o menor e maior preço
                  </span>
                </div>
              )}

              {result.average_price && (
                <div className="glass-card p-5 rounded-2xl border border-gray-800 bg-gray-900/60">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                    <DollarSign className="w-4 h-4 text-blue-400" /> Preço Médio
                  </span>
                  <div className="text-2xl font-black text-white mt-2">
                    {formatBRL(result.average_price)}
                  </div>
                  <span className="text-xs text-gray-400 mt-1 block">
                    Média de mercado entre as lojas
                  </span>
                </div>
              )}

              <div className="glass-card p-5 rounded-2xl border border-gray-800 bg-gray-900/60">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Store className="w-4 h-4 text-indigo-400" /> Lojas Comparadas
                </span>
                <div className="text-2xl font-black text-white mt-2">
                  {result.stores_comparison.length} Lojas
                </div>
                <span className="text-xs text-gray-400 mt-1 block">
                  Amazon, ML, Magalu, KaBuM!, Shopee
                </span>
              </div>
            </div>
          )}

          {/* Tabela Comparativa Oficial Loja a Loja */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Store className="w-5 h-5 text-cyan-400" />
                Comparativo Oficial Loja a Loja
              </h3>
              <span className="text-xs text-gray-400">Ordenado do menor para o maior preço</span>
            </div>

            <div className="overflow-hidden rounded-2xl border border-gray-800 bg-gray-900/90 shadow-xl">
              <div className="divide-y divide-gray-800">
                {result.stores_comparison.map((item, index) => {
                  const redirectUrl = item.deal_id.startsWith("search_")
                    ? item.affiliate_url || item.url
                    : `${API_BASE}/r/${item.deal_id}`;

                  return (
                    <div
                      key={item.deal_id || index}
                      className={`p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-colors ${
                        item.is_lowest
                          ? "bg-emerald-500/5 hover:bg-emerald-500/10"
                          : "hover:bg-gray-800/40"
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 ${
                            item.is_lowest
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-lg shadow-emerald-950"
                              : "bg-gray-800 text-gray-300 border border-gray-700"
                          }`}
                        >
                          #{index + 1}
                        </div>

                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-black text-white">{item.store}</span>
                            {item.is_lowest && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-black uppercase bg-emerald-500 text-black tracking-wider flex items-center gap-1 shadow-sm">
                                <Award className="w-3 h-3" /> Menor Preço
                              </span>
                            )}
                            {item.free_shipping === 1 && (
                              <span className="text-[10px] font-bold text-emerald-400 flex items-center gap-1">
                                <Truck className="w-3 h-3" /> Frete Grátis
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-300 line-clamp-1 max-w-lg mt-0.5">
                            {item.product_title}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between sm:justify-end gap-5">
                        <div className="text-left sm:text-right">
                          <div className="text-lg font-black text-white">
                            {formatBRL(item.price)}
                          </div>
                          {item.price_diff > 0 ? (
                            <span className="text-[11px] font-medium text-rose-400 block">
                              + {formatBRL(item.price_diff)} vs menor
                            </span>
                          ) : item.is_lowest ? (
                            <span className="text-[11px] font-bold text-emerald-400 block">
                              Melhor opção do mercado
                            </span>
                          ) : null}
                        </div>

                        <a
                          href={redirectUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`px-4 py-2.5 rounded-xl font-bold text-xs flex items-center gap-1.5 transition-all shrink-0 ${
                            item.is_lowest
                              ? "bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white shadow-lg shadow-emerald-600/30 hover:scale-105"
                              : "bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700"
                          }`}
                        >
                          Ir para {item.store} <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>

          {/* Todas as Variações e Ofertas Encontradas */}
          {result.items && result.items.length > 0 && (
            <section className="space-y-4 pt-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Flame className="w-5 h-5 text-rose-500" />
                  Todas as Ofertas e Modelos Encontrados ({result.items.length})
                </h3>
                <span className="text-xs text-gray-400">Modelos, cores e variações</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
                {result.items.map((deal) => (
                  <DealCard key={deal.id} deal={deal} />
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {/* Estado Inicial (Sem busca realizada ainda) */}
      {!loading && !result && (
        <div className="glass-card rounded-3xl p-12 text-center space-y-4 border border-gray-800 bg-gray-900/40">
          <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mx-auto text-cyan-400">
            <Bot className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-2">
            <h3 className="text-lg font-bold text-white">Como Funciona a Busca Personalizada?</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Em vez de esperar por alertas passivos, nossos robôs fazem o trabalho pesado por você. Digite qualquer produto acima e nós varremos todos os marketplaces para entregar a lista comparativa com menor preço comprovado.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function CustomSearchPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-gray-400">Carregando busca personalizada...</div>}>
      <SearchContent />
    </Suspense>
  );
}
