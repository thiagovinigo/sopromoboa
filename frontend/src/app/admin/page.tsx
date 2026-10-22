"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Plus,
  Trash2,
  ExternalLink,
  Copy,
  Check,
  TrendingUp,
  Store,
  Link2,
  DollarSign,
  Sparkles,
  MousePointerClick,
  Layers,
  Settings,
  Eye,
  Zap,
  Bot,
  RefreshCw,
  Flame,
  Clock,
  Activity,
  CheckCircle2,
  Play,
} from "lucide-react";
import {
  fetchAdminDeals,
  createAdminDeal,
  deleteAdminDeal,
  fetchAdminStats,
  fetchAffiliates,
  saveAffiliate,
  generateAffiliateLink,
  Deal,
  AdminStats,
  AffiliateProgram,
  WorkerStatus,
  fetchWorkerStatus,
  triggerWorker,
  simulatePriceDrop,
} from "@/lib/api";

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<"anuncios" | "publicar" | "gerador" | "tags" | "metricas" | "workers">("anuncios");

  // Dados
  const [adminDeals, setAdminDeals] = useState<Deal[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [programs, setPrograms] = useState<AffiliateProgram[]>([]);
  const [workerStatus, setWorkerStatus] = useState<WorkerStatus | null>(null);
  const [workerRunning, setWorkerRunning] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<{ success: boolean; message: string; deal?: any } | null>(null);
  const [loading, setLoading] = useState(true);

  // Formulário de Novo Anúncio
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [price, setPrice] = useState("");
  const [listPrice, setListPrice] = useState("");
  const [source, setSource] = useState("Amazon");
  const [category, setCategory] = useState("eletronicos");
  const [imageUrl, setImageUrl] = useState("");
  const [couponCode, setCouponCode] = useState("");
  const [isFeatured, setIsFeatured] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(false);

  // Gerador Rápido
  const [generatorUrl, setGeneratorUrl] = useState("");
  const [campaign, setCampaign] = useState("telegram");
  const [generatedLink, setGeneratedLink] = useState<{ store: string; affiliate_url: string } | null>(null);
  const [copiedLink, setCopiedLink] = useState(false);
  const [copiedDealId, setCopiedDealId] = useState<string | null>(null);

  // Cadastro de Tag
  const [networkSlug, setNetworkSlug] = useState("amazon");
  const [trackingId, setTrackingId] = useState("");
  const [programName, setProgramName] = useState("");
  const [commissionRate, setCommissionRate] = useState("Até 15%");
  const [savingTag, setSavingTag] = useState(false);
  const [tagSuccess, setTagSuccess] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    const [dealsRes, statsRes, progRes, workerRes] = await Promise.all([
      fetchAdminDeals(),
      fetchAdminStats(),
      fetchAffiliates(),
      fetchWorkerStatus(),
    ]);
    setAdminDeals(dealsRes);
    setStats(statsRes);
    setPrograms(progRes);
    setWorkerStatus(workerRes);
    if (workerRes) {
      setWorkerRunning(workerRes.is_running);
    }
    setLoading(false);
  };

  const handleTriggerWorker = async () => {
    setWorkerRunning(true);
    try {
      await triggerWorker();
      let attempts = 0;
      const interval = setInterval(async () => {
        attempts++;
        const updated = await fetchWorkerStatus();
        if (updated) {
          setWorkerStatus(updated);
          if (!updated.is_running || attempts >= 20) {
            clearInterval(interval);
            setWorkerRunning(false);
            loadData();
          }
        }
      }, 1500);
    } catch (err) {
      console.error(err);
      setWorkerRunning(false);
    }
  };

  const handleSimulateDrop = async () => {
    setSimulating(true);
    try {
      const res = await simulatePriceDrop();
      setSimulationResult(res);
      loadData();
      setTimeout(() => setSimulationResult(null), 8000);
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  const handlePublishDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !url.trim() || !price) return;

    setPublishing(true);
    try {
      const res = await createAdminDeal({
        title: title.trim(),
        price: parseFloat(price),
        list_price: listPrice ? parseFloat(listPrice) : undefined,
        source: source,
        url: url.trim(),
        image_url: imageUrl.trim() || undefined,
        category: category,
        coupon_code: couponCode.trim() || undefined,
        is_featured: isFeatured ? 1 : 0,
      });

      if (res) {
        setPublishSuccess(true);
        setTitle("");
        setUrl("");
        setPrice("");
        setListPrice("");
        setImageUrl("");
        setCouponCode("");
        loadData();
        setTimeout(() => {
          setPublishSuccess(false);
          setActiveTab("anuncios");
        }, 1800);
      }
    } finally {
      setPublishing(false);
    }
  };

  const handleDeleteDeal = async (id: string) => {
    if (confirm("Deseja realmente remover este anúncio de afiliado?")) {
      await deleteAdminDeal(id);
      loadData();
    }
  };

  const handleGenerateLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!generatorUrl.trim()) return;
    const res = await generateAffiliateLink(generatorUrl.trim(), campaign);
    setGeneratedLink(res);
  };

  const handleSaveProgram = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackingId.trim()) return;
    setSavingTag(true);
    try {
      await saveAffiliate({
        name: programName || networkSlug.toUpperCase(),
        network_slug: networkSlug,
        tracking_id: trackingId.trim(),
        commission_rate: commissionRate,
      });
      setTagSuccess(true);
      setTrackingId("");
      setProgramName("");
      loadData();
      setTimeout(() => setTagSuccess(false), 2500);
    } finally {
      setSavingTag(false);
    }
  };

  const formatBRL = (val: number) =>
    val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  return (
    <div className="space-y-8">
      {/* Header do Painel Admin */}
      <div className="relative overflow-hidden rounded-3xl p-8 border border-emerald-500/30 bg-gradient-to-r from-emerald-950/40 via-gray-900/80 to-gray-900/90 shadow-2xl">
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-black uppercase tracking-wider">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            Painel do Administrador & Monetização
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Central de Anúncios com <br />
            <span className="text-emerald-400">Nossos Links de Afiliados</span>
          </h1>
          <p className="text-sm text-gray-300">
            Gerencie os anúncios monetizados que aparecem com seus links diretos de afiliado, acompanhe cliques contabilizados em tempo real e gere links para redes sociais.
          </p>
        </div>
      </div>

      {/* Cards de Métricas no Topo */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-5 border border-gray-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-gray-400 block">Nossos Anúncios Ativos</span>
            <span className="text-2xl font-black text-white">{adminDeals.length}</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold">
            ★
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-gray-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-gray-400 block">Total de Cliques de Afiliados</span>
            <span className="text-2xl font-black text-emerald-400">{stats?.total_clicks || 0}</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <MousePointerClick className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-gray-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-gray-400 block">Lojas de Afiliados Conectadas</span>
            <span className="text-2xl font-black text-amber-400">{programs.length}</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Store className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Navegação por Abas do Painel */}
      <div className="flex items-center gap-2 overflow-x-auto border-b border-gray-800 pb-3">
        <button
          onClick={() => setActiveTab("anuncios")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "anuncios"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Layers className="w-4 h-4" /> Nossos Anúncios ({adminDeals.length})
        </button>

        <button
          onClick={() => setActiveTab("publicar")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "publicar"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Plus className="w-4 h-4" /> + Publicar Anúncio Afiliado
        </button>

        <button
          onClick={() => setActiveTab("gerador")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "gerador"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Link2 className="w-4 h-4" /> Gerador Rápido de Links
        </button>

        <button
          onClick={() => setActiveTab("tags")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "tags"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Settings className="w-4 h-4" /> Tags de Parceiros
        </button>

        <button
          onClick={() => setActiveTab("metricas")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "metricas"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <TrendingUp className="w-4 h-4" /> Métricas de Conversão
        </button>

        <button
          onClick={() => setActiveTab("workers")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "workers"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Bot className="w-4 h-4" /> Robôs & Workers
          {workerStatus?.is_running && (
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          )}
        </button>
      </div>

      {/* CONTEÚDO DAS ABAS */}

      {/* ABA 1: NOSSOS ANÚNCIOS AFILIADOS */}
      {activeTab === "anuncios" && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-400" />
              Anúncios Cadastrados com Nossos Links ({adminDeals.length})
            </h2>
            <button
              onClick={() => setActiveTab("publicar")}
              className="px-3.5 py-1.5 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" /> Novo Anúncio
            </button>
          </div>

          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="glass-card rounded-2xl h-24 animate-pulse bg-gray-800/40" />
              ))}
            </div>
          ) : adminDeals.length === 0 ? (
            <div className="glass-card rounded-3xl p-12 text-center space-y-4">
              <DollarSign className="w-12 h-12 text-gray-600 mx-auto" />
              <h3 className="font-bold text-white text-lg">Nenhum anúncio afiliado cadastrado ainda</h3>
              <p className="text-xs text-gray-400 max-w-sm mx-auto">
                Cadastre suas primeiras ofertas monetizadas para que apareçam em destaque na vitrine com sua tag de comissão.
              </p>
              <button
                onClick={() => setActiveTab("publicar")}
                className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-600 shadow-md shadow-emerald-600/30"
              >
                Cadastrar Primeiro Anúncio
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {adminDeals.map((deal) => (
                <div
                  key={deal.id}
                  className="glass-card rounded-2xl p-4 border border-gray-800 hover:border-emerald-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-4">
                    {deal.image_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={deal.image_url}
                        alt={deal.title}
                        className="w-16 h-16 object-contain bg-gray-900 rounded-xl p-1 border border-gray-800"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-xl bg-gray-900 border border-gray-800 flex items-center justify-center text-xs text-gray-600">
                        Sem foto
                      </div>
                    )}
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-md">
                          {deal.source}
                        </span>
                        {deal.discount_percent > 0 && (
                          <span className="text-[10px] font-black text-white flame-gradient px-1.5 py-0.5 rounded-md">
                            -{deal.discount_percent}% OFF
                          </span>
                        )}
                        <span className="text-[10px] text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded-md font-semibold">
                          Nossa Curadoria
                        </span>
                      </div>
                      <h3 className="font-bold text-sm text-white line-clamp-1">{deal.title}</h3>
                      <div className="flex items-center gap-3 text-xs">
                        <span className="font-black text-emerald-400">{formatBRL(deal.price)}</span>
                        {deal.list_price && (
                          <span className="text-gray-500 line-through text-[11px]">{formatBRL(deal.list_price)}</span>
                        )}
                        <span className="text-gray-400 flex items-center gap-1 text-[11px]">
                          <MousePointerClick className="w-3.5 h-3.5 text-gray-400" />
                          {deal.clicks_count || 0} cliques gerados
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center">
                    <button
                      onClick={() => {
                        const link = deal.affiliate_url || deal.url;
                        navigator.clipboard.writeText(link);
                        setCopiedDealId(deal.id);
                        setTimeout(() => setCopiedDealId(null), 2000);
                      }}
                      className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20 text-emerald-300 text-xs font-semibold flex items-center gap-1 transition-colors"
                      title="Copiar link comissionado para redes"
                    >
                      {copiedDealId === deal.id ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" /> Copiado!
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" /> Copiar Link
                        </>
                      )}
                    </button>
                    <a
                      href={deal.affiliate_url || deal.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white text-xs font-semibold flex items-center gap-1"
                    >
                      Ver Link <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                    <button
                      onClick={() => handleDeleteDeal(deal.id)}
                      className="p-2 rounded-xl bg-gray-800 hover:bg-rose-500/20 text-gray-400 hover:text-rose-400 border border-gray-700 transition-colors"
                      title="Excluir anúncio"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* ABA 2: PUBLICAR NOVO ANÚNCIO AFILIADO */}
      {activeTab === "publicar" && (
        <section className="glass-card rounded-3xl p-6 sm:p-8 max-w-2xl mx-auto space-y-5 border border-emerald-500/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Plus className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Publicar Anúncio com Nosso Link Afiliado</h2>
              <p className="text-xs text-gray-400">A tag do parceiro configurada será injetada automaticamente</p>
            </div>
          </div>

          <form onSubmit={handlePublishDeal} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Link do Produto na Loja (Amazon, Magalu, Mercado Livre, etc.) *
              </label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.amazon.com.br/dp/..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Título do Anúncio *
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Ex: Console PlayStation 5 Slim 1TB + 2 Jogos"
                className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">
                  Preço em Promoção (R$) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  placeholder="Ex: 3199.00"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">
                  Preço Original 'De' (R$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={listPrice}
                  onChange={(e) => setListPrice(e.target.value)}
                  placeholder="Ex: 3799.00"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Loja de Origem</label>
                <select
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs font-semibold focus:outline-none focus:border-emerald-500"
                >
                  <option value="Amazon">Amazon Brasil</option>
                  <option value="Mercado Livre">Mercado Livre</option>
                  <option value="Magazine Luiza">Magazine Luiza</option>
                  <option value="KaBuM!">KaBuM!</option>
                  <option value="Shopee">Shopee</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Categoria</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs font-semibold focus:outline-none focus:border-emerald-500"
                >
                  <option value="smartphones">Smartphones</option>
                  <option value="informatica">Informática</option>
                  <option value="eletronicos">Eletrônicos</option>
                  <option value="games">Games</option>
                  <option value="eletrodomesticos">Eletrodomésticos</option>
                  <option value="casa">Casa & Cozinha</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">URL da Imagem</label>
                <input
                  type="url"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  placeholder="https://...jpg"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Cupom Opcional</label>
                <input
                  type="text"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value)}
                  placeholder="Ex: PROMO10"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs focus:outline-none focus:border-emerald-500 uppercase"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <input
                type="checkbox"
                id="isFeatured"
                checked={isFeatured}
                onChange={(e) => setIsFeatured(e.target.checked)}
                className="w-4 h-4 rounded text-emerald-600 bg-gray-900 border-gray-700"
              />
              <label htmlFor="isFeatured" className="text-xs text-gray-300 font-semibold cursor-pointer">
                Destacar anúncio no topo da vitrine com selo de recomendação
              </label>
            </div>

            {publishSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 text-xs font-bold flex items-center gap-2">
                <Check className="w-4 h-4" /> Anúncio publicado com link de afiliado ativo!
              </div>
            )}

            <button
              type="submit"
              disabled={publishing}
              className="w-full py-3 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-600 shadow-md shadow-emerald-600/30 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <DollarSign className="w-4 h-4" />
              {publishing ? "Publicando..." : "Publicar Anúncio Comissionado"}
            </button>
          </form>
        </section>
      )}

      {/* ABA 3: GERADOR RÁPIDO */}
      {activeTab === "gerador" && (
        <section className="glass-card rounded-3xl p-6 sm:p-8 max-w-2xl mx-auto space-y-5 border border-emerald-500/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Link2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Gerador Rápido de Links de Afiliados</h2>
              <p className="text-xs text-gray-400">Converta links para divulgar no WhatsApp, Telegram e redes sociais</p>
            </div>
          </div>

          <form onSubmit={handleGenerateLink} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Link do Produto
              </label>
              <input
                type="url"
                required
                value={generatorUrl}
                onChange={(e) => setGeneratorUrl(e.target.value)}
                placeholder="https://www.amazon.com.br/dp/..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Origem da Campanha (UTM Medium)
              </label>
              <select
                value={campaign}
                onChange={(e) => setCampaign(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs font-semibold focus:outline-none focus:border-emerald-500"
              >
                <option value="telegram">Canal do Telegram</option>
                <option value="whatsapp">Grupo de Ofertas no WhatsApp</option>
                <option value="instagram">Instagram Stories / Bio</option>
                <option value="tiktok">TikTok / Vídeos</option>
                <option value="site">Radar Só Promo Boa</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-600 shadow-md shadow-emerald-600/30 flex items-center justify-center gap-2"
            >
              <Link2 className="w-4 h-4" /> Gerar Link Comissionado
            </button>
          </form>

          {generatedLink && (
            <div className="p-4 rounded-2xl bg-gray-900/90 border border-emerald-500/40 space-y-3 animate-fade-in">
              <span className="font-bold text-xs text-emerald-400 uppercase">
                Loja: {generatedLink.store} ✓ Tag Injetada
              </span>
              <div className="relative">
                <input
                  type="text"
                  readOnly
                  value={generatedLink.affiliate_url}
                  className="w-full pr-24 pl-3 py-2 text-xs font-mono bg-black/60 border border-gray-700 rounded-lg text-emerald-300 focus:outline-none truncate"
                />
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(generatedLink.affiliate_url);
                    setCopiedLink(true);
                    setTimeout(() => setCopiedLink(false), 2000);
                  }}
                  className="absolute right-1 top-1 bottom-1 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-md text-xs font-bold flex items-center gap-1"
                >
                  {copiedLink ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  {copiedLink ? "Copiado!" : "Copiar"}
                </button>
              </div>
            </div>
          )}
        </section>
      )}

      {/* ABA 4: TAGS DE PARCEIROS */}
      {activeTab === "tags" && (
        <section className="glass-card rounded-3xl p-6 sm:p-8 max-w-3xl mx-auto space-y-5 border border-emerald-500/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Configurar Nossas Tags de Parceiros</h2>
              <p className="text-xs text-gray-400">Define suas credenciais de comissão nas plataformas</p>
            </div>
          </div>

          <form onSubmit={handleSaveProgram} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Marketplace / Loja</label>
                <select
                  value={networkSlug}
                  onChange={(e) => setNetworkSlug(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs font-semibold focus:outline-none focus:border-blue-500"
                >
                  <option value="amazon">Amazon Brasil Associados</option>
                  <option value="magalu">Parceiro Magalu</option>
                  <option value="mercadolivre">Mercado Livre Afiliados</option>
                  <option value="kabum">KaBuM! Afiliados</option>
                  <option value="shopee">Shopee Afiliados</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Tag de Afiliado (Tracking ID) *</label>
                <input
                  type="text"
                  required
                  value={trackingId}
                  onChange={(e) => setTrackingId(e.target.value)}
                  placeholder="Ex: sopromoboa-20"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            {tagSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 text-xs font-bold flex items-center gap-2">
                <Check className="w-4 h-4" /> Tag salva e integrada com sucesso!
              </div>
            )}

            <button
              type="submit"
              disabled={savingTag}
              className="w-full py-2.5 rounded-xl font-bold text-xs text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 transition-colors"
            >
              {savingTag ? "Salvando..." : "Salvar Configuração de Tag"}
            </button>
          </form>

          {/* Lista de Tags Configuradas */}
          <div className="space-y-2 pt-2">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Tags Ativas ({programs.length})</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {programs.map((p) => (
                <div key={p.id} className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-white text-xs block">{p.name}</span>
                    <span className="text-[11px] font-mono text-emerald-400">Tag: {p.tracking_id}</span>
                  </div>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-md font-semibold">
                    {p.commission_rate || "Ativo"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ABA 5: MÉTRICAS DE CONVERSÃO */}
      {activeTab === "metricas" && (
        <section className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Cliques por Loja */}
            <div className="glass-card rounded-3xl p-6 border border-gray-800 space-y-4">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <Store className="w-4 h-4 text-emerald-400" />
                Cliques por Loja
              </h3>
              {stats?.clicks_by_store && stats.clicks_by_store.length > 0 ? (
                <div className="space-y-2">
                  {stats.clicks_by_store.map((s) => (
                    <div key={s.store} className="flex items-center justify-between p-2.5 rounded-xl bg-gray-900/60 text-xs">
                      <span className="font-semibold text-white">{s.store}</span>
                      <span className="font-bold text-emerald-400">{s.clicks} cliques</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">Nenhum clique registrado ainda.</p>
              )}
            </div>

            {/* Anúncios Mais Clicados */}
            <div className="glass-card rounded-3xl p-6 border border-gray-800 space-y-4">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-rose-400" />
                Anúncios Mais Acessados
              </h3>
              {stats?.top_clicked_deals && stats.top_clicked_deals.length > 0 ? (
                <div className="space-y-2">
                  {stats.top_clicked_deals.map((t) => (
                    <div key={t.id} className="flex items-center justify-between p-2.5 rounded-xl bg-gray-900/60 text-xs">
                      <span className="font-semibold text-white line-clamp-1 max-w-[200px]">{t.title}</span>
                      <span className="font-bold text-emerald-400">{t.clicks} cliques</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">Os anúncios mais clicados aparecerão aqui conforme os usuários acessarem.</p>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ABA 6: ROBÔS & WORKERS (ACOMPANHAMENTO DE OFERTAS) */}
      {activeTab === "workers" && (
        <section className="space-y-6">
          {/* Banner de Feedback de Simulação */}
          {simulationResult && (
            <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/80 to-gray-900 border border-emerald-500/40 text-white flex items-center justify-between shadow-xl animate-in fade-in">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <span className="font-bold text-sm block text-emerald-300">{simulationResult.message}</span>
                  {simulationResult.deal && (
                    <span className="text-xs text-gray-400">
                      Preço caiu de <span className="line-through">{formatBRL(simulationResult.deal.old_price)}</span> para <strong className="text-white">{formatBRL(simulationResult.deal.new_price)}</strong> (-{simulationResult.deal.discount_percent}% OFF). Verifique na página do <a href="/radar" target="_blank" className="text-emerald-400 underline font-semibold">Radar de Quedas</a>!
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => setSimulationResult(null)}
                className="text-gray-400 hover:text-white text-xs px-2 py-1"
              >
                ✕
              </button>
            </div>
          )}

          {/* Card Principal de Status e Controle */}
          <div className="glass-card rounded-3xl p-6 border border-gray-800 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${workerRunning ? "bg-amber-400 animate-ping" : "bg-emerald-400"}`} />
                  <span className="text-sm font-black text-white uppercase tracking-wider">
                    {workerRunning ? "Varredura em Execução no Servidor..." : "Robôs em Espera / Prontos"}
                  </span>
                </div>
                <p className="text-xs text-gray-400">
                  O worker executa periodicamente a cada {workerStatus?.interval_minutes || 15} minutos em background thread, comparando preços, detectando quedas reais e gravando o histórico.
                </p>
                {workerStatus?.last_run && (
                  <div className="text-[11px] text-gray-500 flex items-center gap-2 pt-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Última varredura concluída em: {new Date(workerStatus.last_run).toLocaleTimeString("pt-BR")}</span>
                  </div>
                )}
              </div>

              {/* Botões de Ação */}
              <div className="flex items-center gap-2 flex-wrap">
                <button
                  onClick={handleSimulateDrop}
                  disabled={simulating}
                  className="px-4 py-2.5 rounded-xl font-bold text-xs text-white bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 transition-all flex items-center gap-1.5 shadow-sm"
                  title="Aplica uma oscilação de preço real em um produto para testar o Radar e os Alertas"
                >
                  <Flame className="w-4 h-4 text-rose-500" />
                  {simulating ? "Simulando..." : "Simular Queda de Preço"}
                </button>

                <button
                  onClick={handleTriggerWorker}
                  disabled={workerRunning}
                  className="px-5 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-600 transition-all flex items-center gap-2 shadow-lg shadow-emerald-600/20 disabled:opacity-60"
                >
                  <RefreshCw className={`w-4 h-4 ${workerRunning ? "animate-spin" : ""}`} />
                  {workerRunning ? "Varrendo Ofertas..." : "Executar Varredura Agora"}
                </button>
              </div>
            </div>

            {/* Grid de Métricas de Operação */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800">
                <span className="text-[11px] font-semibold text-gray-400 block">Total Monitorado</span>
                <span className="text-xl font-black text-white">{workerStatus?.total_monitored || 0}</span>
                <span className="text-[10px] text-gray-500 block">no banco de dados</span>
              </div>

              <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800">
                <span className="text-[11px] font-semibold text-gray-400 block">Quedas Ativas</span>
                <span className="text-xl font-black text-rose-400">{workerStatus?.total_active_drops || 0}</span>
                <span className="text-[10px] text-gray-500 block">visíveis no Radar</span>
              </div>

              <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800">
                <span className="text-[11px] font-semibold text-gray-400 block">Última Rodada</span>
                <span className="text-xl font-black text-emerald-400">{workerStatus?.last_stats?.updated || 0}</span>
                <span className="text-[10px] text-gray-500 block">produtos atualizados</span>
              </div>

              <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800">
                <span className="text-[11px] font-semibold text-gray-400 block">Alertas Disparados</span>
                <span className="text-xl font-black text-amber-400">{workerStatus?.last_stats?.alerts_triggered || 0}</span>
                <span className="text-[10px] text-gray-500 block">correspondências de preço</span>
              </div>
            </div>
          </div>

          {/* Robôs Ativos & Configuração */}
          <div className="space-y-3">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <Bot className="w-4 h-4 text-emerald-400" />
              Robôs e Fontes de Ingestão Ativas
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {(workerStatus?.active_scrapers || [
                { name: "Gatry Real Deals (Páginas 1 a 4)", target: "Amazon, Magalu, ML, KaBuM", status: "Ativo", interval: "15 min" },
                { name: "Curated Golden Deals", target: "Top 32 Ofertas Auditadas", status: "Ativo", interval: "15 min" },
                { name: "Targeted Price Tracker", target: "Histórico & Alertas de Usuários", status: "Ativo", interval: "Contínuo" }
              ]).map((s, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-white">{s.name}</span>
                    <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
                      {s.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-400">
                    Alvo: <strong className="text-gray-300">{s.target}</strong>
                  </p>
                  <div className="text-[10px] text-gray-500 flex items-center gap-1">
                    <Activity className="w-3 h-3 text-emerald-500" />
                    <span>Ciclo: a cada {s.interval}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Histórico Recente de Execuções */}
          <div className="glass-card rounded-3xl p-6 border border-gray-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <Clock className="w-4 h-4 text-emerald-400" />
                Histórico Recente de Varreduras
              </h3>
              <span className="text-xs text-gray-400">Últimas execuções registradas</span>
            </div>

            {workerStatus?.history && workerStatus.history.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="text-gray-400 border-b border-gray-800">
                      <th className="pb-3 font-semibold">Horário</th>
                      <th className="pb-3 font-semibold">Tipo</th>
                      <th className="pb-3 font-semibold">Duração</th>
                      <th className="pb-3 font-semibold">Novas Ofertas</th>
                      <th className="pb-3 font-semibold">Atualizadas</th>
                      <th className="pb-3 font-semibold">Quedas Detectadas</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60">
                    {workerStatus.history.map((h, i) => (
                      <tr key={i} className="hover:bg-gray-800/20">
                        <td className="py-2.5 font-mono text-gray-300">
                          {new Date(h.timestamp).toLocaleTimeString("pt-BR")}
                        </td>
                        <td className="py-2.5">
                          <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                            h.type === "manual" ? "bg-purple-500/20 text-purple-300" : "bg-emerald-500/20 text-emerald-300"
                          }`}>
                            {h.type === "manual" ? "Manual" : "Agendado"}
                          </span>
                        </td>
                        <td className="py-2.5 font-semibold text-gray-400">
                          {h.duration_seconds ? `${h.duration_seconds}s` : "-"}
                        </td>
                        <td className="py-2.5 font-bold text-white">
                          {h.stats?.inserted ?? 0}
                        </td>
                        <td className="py-2.5 font-bold text-emerald-400">
                          {h.stats?.updated ?? 0}
                        </td>
                        <td className="py-2.5 font-bold text-rose-400">
                          {h.stats?.price_drops ?? 0}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-6 text-gray-500 text-xs">
                Nenhum histórico registrado ainda. Clique em "Executar Varredura Agora" para iniciar.
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
