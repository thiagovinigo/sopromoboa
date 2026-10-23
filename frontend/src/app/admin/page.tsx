"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
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
  EyeOff,
  Zap,
  Bot,
  RefreshCw,
  Flame,
  Clock,
  Activity,
  CheckCircle2,
  Play,
  Compass,
  ShieldCheck,
  Award,
  XCircle,
  Search,
  Globe,
  Percent,
  Star,
  Lock,
  Key,
  LogOut,
  ShoppingBag,
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
  DiscoveredStore,
  HunterStats,
  fetchHunterStores,
  fetchHunterStats,
  runHunterCycle,
  approveHunterStore,
  rejectHunterStore,
  auditCustomStoreUrl,
  authenticateAdmin,
} from "@/lib/api";

export default function AdminPage() {
  // Autenticação Mestra do Painel Admin (Senha: !Thi5361206)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [authChecking, setAuthChecking] = useState<boolean>(true);
  const [passwordInput, setPasswordInput] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [authError, setAuthError] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);

  const [activeTab, setActiveTab] = useState<
    "anuncios" | "publicar" | "gerador" | "tags" | "metricas" | "workers" | "hunter" | "cadastro_afiliados"
  >("cadastro_afiliados");

  // Dados
  const [adminDeals, setAdminDeals] = useState<Deal[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [programs, setPrograms] = useState<AffiliateProgram[]>([]);
  const [workerStatus, setWorkerStatus] = useState<WorkerStatus | null>(null);
  const [workerRunning, setWorkerRunning] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<{ success: boolean; message: string; deal?: any } | null>(null);
  const [loading, setLoading] = useState(true);

  // Estados do Agente Caçador de Lojas AI
  const [hunterStores, setHunterStores] = useState<DiscoveredStore[]>([]);
  const [hunterStats, setHunterStats] = useState<HunterStats | null>(null);
  const [hunterFilter, setHunterFilter] = useState<"pending" | "approved" | "rejected" | "all">("pending");
  const [hunterSearch, setHunterSearch] = useState("");
  const [hunterRunning, setHunterRunning] = useState(false);
  const [hunterSuccessMsg, setHunterSuccessMsg] = useState("");
  const [customAuditUrl, setCustomAuditUrl] = useState("");
  const [customAuditName, setCustomAuditName] = useState("");
  const [auditing, setAuditing] = useState(false);
  const [auditMsg, setAuditMsg] = useState("");

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
  const [isLightningDeal, setIsLightningDeal] = useState(true);
  const [autoFilledNotice, setAutoFilledNotice] = useState<string | null>(null);
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

  // Tags rápidas no diretório de afiliados
  const [quickTags, setQuickTags] = useState<Record<string, string>>({});
  const [quickSavedSlug, setQuickSavedSlug] = useState<string | null>(null);

  useEffect(() => {
    const saved = typeof window !== "undefined" ? sessionStorage.getItem("sopromoboa_admin_auth") : null;
    if (saved === "true") {
      setIsAuthenticated(true);
      loadData();
      loadHunterData();
    }
    setAuthChecking(false);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingIn(true);
    setAuthError("");
    try {
      const res = await authenticateAdmin(passwordInput.trim());
      if (res.success) {
        if (typeof window !== "undefined") {
          sessionStorage.setItem("sopromoboa_admin_auth", "true");
        }
        setIsAuthenticated(true);
        setPasswordInput("");
        loadData();
        loadHunterData();
      } else {
        setAuthError(res.message || "Senha incorreta. Acesso não autorizado.");
      }
    } catch {
      setAuthError("Erro na autenticação.");
    } finally {
      setLoggingIn(false);
    }
  };

  const handleLogout = () => {
    if (typeof window !== "undefined") {
      sessionStorage.removeItem("sopromoboa_admin_auth");
    }
    setIsAuthenticated(false);
  };

  const handleSaveQuickTag = async (slug: string, name: string, commission: string) => {
    const tagVal = quickTags[slug]?.trim();
    if (!tagVal) return;
    try {
      await saveAffiliate({
        name,
        network_slug: slug,
        tracking_id: tagVal,
        commission_rate: commission,
      });
      setQuickSavedSlug(slug);
      loadData();
      setTimeout(() => setQuickSavedSlug(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

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
    if (progRes && Array.isArray(progRes)) {
      const initialTags: Record<string, string> = { amazon: "thiagovinigo-20" };
      progRes.forEach((p: any) => {
        if (p.network_slug && p.tracking_id) {
          initialTags[p.network_slug] = p.tracking_id;
        }
      });
      setQuickTags((prev) => ({ ...initialTags, ...prev }));
    }
    setWorkerStatus(workerRes);
    if (workerRes) {
      setWorkerRunning(workerRes.is_running);
    }
    setLoading(false);
  };

  const loadHunterData = async () => {
    const [stores, hStats] = await Promise.all([
      fetchHunterStores("all"),
      fetchHunterStats(),
    ]);
    setHunterStores(stores);
    setHunterStats(hStats);
  };

  const handleRunHunter = async () => {
    setHunterRunning(true);
    setHunterSuccessMsg("Store Hunter AI vasculhando a internet por lojas com selo RA1000/Ebit...");
    try {
      const res = await runHunterCycle();
      setHunterSuccessMsg(res.message || "Varredura concluída!");
      await loadHunterData();
      setTimeout(() => setHunterSuccessMsg(""), 6000);
    } catch {
      setHunterSuccessMsg("Erro ao executar varredura do agente.");
      setTimeout(() => setHunterSuccessMsg(""), 4000);
    } finally {
      setHunterRunning(false);
    }
  };

  const handleApproveStore = async (storeId: number) => {
    try {
      await approveHunterStore(storeId);
      await loadHunterData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRejectStore = async (storeId: number) => {
    try {
      await rejectHunterStore(storeId);
      await loadHunterData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAuditCustomUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customAuditUrl) return;
    setAuditing(true);
    setAuditMsg("Agente auditando SSL, domínio e reputação...");
    try {
      const res = await auditCustomStoreUrl(customAuditUrl, customAuditName);
      if (res.already_exists) {
        setAuditMsg(`Loja já catalogada com Trust Score de ${res.store.trust_score}%.`);
      } else {
        setAuditMsg(`Loja '${res.name}' auditada! Trust Score: ${res.trust_score}%. Adicionada para aprovação.`);
        setCustomAuditUrl("");
        setCustomAuditName("");
        await loadHunterData();
      }
      setTimeout(() => setAuditMsg(""), 6000);
    } catch {
      setAuditMsg("Erro ao auditar loja.");
      setTimeout(() => setAuditMsg(""), 4000);
    } finally {
      setAuditing(false);
    }
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

  const handleAutoFillFromUrl = (rawUrl: string) => {
    setUrl(rawUrl);
    if (!rawUrl) return;

    if (rawUrl.includes("amazon.com.br")) {
      setSource("Amazon");
      const asinMatch = rawUrl.match(/\/(?:dp|gp\/product|d)\/([A-Z0-9]{10})/i);
      const asin = asinMatch ? asinMatch[1] : null;

      if (asin) {
        setImageUrl(`https://m.media-amazon.com/images/P/${asin}.01._SCLZZZZZZZ_SX500_.jpg`);
      }

      const slugMatch = rawUrl.match(/amazon\.com\.br\/([^/?#]+)\/dp\//i);
      if (slugMatch) {
        const decoded = decodeURIComponent(slugMatch[1]).replace(/-/g, " ");
        if (decoded.length > 3 && !decoded.startsWith("dp")) {
          setTitle(decoded);
          const lower = decoded.toLowerCase();
          if (lower.includes("iphone") || lower.includes("celular") || lower.includes("galaxy")) {
            setCategory("smartphones");
          } else if (lower.includes("creatina") || lower.includes("whey") || lower.includes("suplemento")) {
            setCategory("saude");
          } else if (lower.includes("air fryer") || lower.includes("panela") || lower.includes("cafeteira") || lower.includes("aspirador")) {
            setCategory("eletrodomesticos");
          } else if (lower.includes("fire tv") || lower.includes("echo") || lower.includes("alexa") || lower.includes("tv")) {
            setCategory("eletronicos");
          } else if (lower.includes("notebook") || lower.includes("monitor") || lower.includes("ssd") || lower.includes("mouse")) {
            setCategory("informatica");
          } else if (lower.includes("playstation") || lower.includes("ps5") || lower.includes("xbox") || lower.includes("nintendo")) {
            setCategory("games");
          } else if (lower.includes("kindle") || lower.includes("livro")) {
            setCategory("livros");
          }
        }
      }

      setIsLightningDeal(true);
      setAutoFilledNotice("⚡ Link da Amazon analisado! Título, imagem e tag 'thiagovinigo-20' preparados automaticamente.");
      setTimeout(() => setAutoFilledNotice(null), 8000);
    } else if (rawUrl.includes("magazineluiza.com.br")) {
      setSource("Magazine Luiza");
    } else if (rawUrl.includes("mercadolivre.com.br")) {
      setSource("Mercado Livre");
    } else if (rawUrl.includes("kabum.com.br")) {
      setSource("KaBuM!");
    } else if (rawUrl.includes("shopee.com.br")) {
      setSource("Shopee");
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
        is_lightning_deal: isLightningDeal ? 1 : 0,
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

  // TELA DE VERIFICAÇÃO / LOADING INICIAL
  if (authChecking) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex items-center gap-3 text-emerald-400 text-sm font-semibold animate-pulse">
          <Flame className="w-5 h-5 animate-spin" /> Verificando credenciais de acesso...
        </div>
      </div>
    );
  }

  // TELA DE BLOQUEIO / LOGIN COM SENHA MESTRA (!Thi5361206)
  if (!isAuthenticated) {
    return (
      <div className="min-h-[75vh] flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md relative">
          <div className="absolute -inset-1 rounded-3xl bg-gradient-to-r from-emerald-500 via-rose-500 to-amber-500 opacity-20 blur-xl animate-pulse" />
          
          <div className="relative glass-card rounded-3xl p-7 sm:p-8 border border-gray-800 bg-[#0d131f]/95 shadow-2xl space-y-6">
            <div className="text-center space-y-3">
              <div className="w-16 h-16 rounded-2xl flame-gradient mx-auto flex items-center justify-center text-white shadow-xl shadow-rose-500/30">
                <Lock className="w-8 h-8" />
              </div>
              <h1 className="text-2xl font-black text-white tracking-tight">
                Painel Restrito Só Promo Boa
              </h1>
              <p className="text-xs text-gray-400 leading-relaxed">
                Área exclusiva de administração, credenciamento de afiliados e inteligência do sistema. Digite a senha mestra para acessar.
              </p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-gray-300 block mb-1.5 flex items-center gap-1.5">
                  <Key className="w-3.5 h-3.5 text-emerald-400" /> Senha Mestra do Administrador
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={passwordInput}
                    onChange={(e) => {
                      setPasswordInput(e.target.value);
                      if (authError) setAuthError("");
                    }}
                    placeholder="Digite a senha mestra..."
                    className="w-full bg-gray-950/90 border border-gray-700 focus:border-emerald-500 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none transition-all pr-11 font-mono tracking-wider"
                    autoFocus
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors p-1"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {authError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400" />
                  <span>{authError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loggingIn || !passwordInput}
                className="w-full py-3.5 rounded-xl font-black text-sm bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white shadow-xl shadow-emerald-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loggingIn ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" /> Verificando...
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4" /> Desbloquear Painel Admin
                  </>
                )}
              </button>
            </form>

            <div className="text-center pt-2 border-t border-gray-800/80">
              <Link href="/" className="text-xs text-gray-400 hover:text-white transition-colors">
                ← Voltar para a página inicial
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header do Painel Admin */}
      <div className="relative overflow-hidden rounded-3xl p-8 border border-emerald-500/30 bg-gradient-to-r from-emerald-950/40 via-gray-900/80 to-gray-900/90 shadow-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-black uppercase tracking-wider">
              <DollarSign className="w-4 h-4 text-emerald-400" />
              Painel do Administrador & Monetização
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              Central de Afiliados & <br />
              <span className="text-emerald-400">Melhores Lojas do Brasil</span>
            </h1>
            <p className="text-sm text-gray-300">
              Gerencie seus links de afiliado, cadastre-se nas lojas líderes, audite lojas da internet com IA e acompanhe seus ganhos em tempo real.
            </p>
          </div>

          <button
            onClick={handleLogout}
            className="self-start sm:self-center px-4 py-2.5 rounded-xl bg-gray-800/90 hover:bg-rose-500/20 text-gray-300 hover:text-rose-300 border border-gray-700 hover:border-rose-500/40 text-xs font-bold transition-all flex items-center gap-2 shrink-0 shadow-lg"
            title="Bloquear e sair do painel"
          >
            <LogOut className="w-4 h-4" />
            Sair do Painel
          </button>
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
          onClick={() => setActiveTab("cadastro_afiliados")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
            activeTab === "cadastro_afiliados"
              ? "bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 text-white shadow-lg shadow-orange-500/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <ShoppingBag className="w-4 h-4 text-amber-300" /> 🚀 Cadastro em Lojas de Afiliados
        </button>

        <button
          onClick={() => setActiveTab("hunter")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
            activeTab === "hunter"
              ? "bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-indigo-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Compass className={`w-4 h-4 ${hunterRunning ? "animate-spin text-violet-400" : "text-violet-400"}`} />
          Caçador de Lojas AI
          {hunterStats && hunterStats.pending_approval > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] font-black bg-amber-500 text-gray-950">
              {hunterStats.pending_approval}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("anuncios")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
            activeTab === "anuncios"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Layers className="w-4 h-4" /> Nossos Anúncios ({adminDeals.length})
        </button>

        <button
          onClick={() => setActiveTab("publicar")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
            activeTab === "publicar"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Plus className="w-4 h-4" /> + Publicar Anúncio Afiliado
        </button>

        <button
          onClick={() => setActiveTab("gerador")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
            activeTab === "gerador"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Link2 className="w-4 h-4" /> Gerador Rápido de Links
        </button>

        <button
          onClick={() => setActiveTab("tags")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
            activeTab === "tags"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <Settings className="w-4 h-4" /> Tags de Parceiros
        </button>

        <button
          onClick={() => setActiveTab("metricas")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
            activeTab === "metricas"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
              : "bg-gray-800/80 text-gray-400 hover:text-white"
          }`}
        >
          <TrendingUp className="w-4 h-4" /> Métricas de Conversão
        </button>

        <button
          onClick={() => setActiveTab("workers")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
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
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>Publicar Anúncio com Nosso Link Afiliado</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  ⚡ Auto-Tag thiagovinigo-20
                </span>
              </h2>
              <p className="text-xs text-gray-400">Cole o link da Amazon ou de parceiros. Título e imagem são preenchidos automaticamente!</p>
            </div>
          </div>

          {/* Dica Expressa de Cadastrar Oferta Relâmpago */}
          <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-2">
            <div className="flex items-center gap-2 text-amber-300 text-xs font-bold">
              <Zap className="w-4 h-4 fill-amber-400 text-amber-400" />
              <span>Método Rápido: Cadastrar uma Oferta Relâmpago da Amazon</span>
            </div>
            <p className="text-xs text-gray-300 leading-relaxed">
              Viu uma super promoção na Amazon? Copie o link do produto no navegador e cole no campo abaixo. O sistema detecta o nome do produto, busca a foto oficial e garante que a sua tag de comissão <strong>thiagovinigo-20</strong> seja aplicada na hora!
            </p>
          </div>

          {autoFilledNotice && (
            <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center gap-2 animate-fadeIn">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>{autoFilledNotice}</span>
            </div>
          )}

          <form onSubmit={handlePublishDeal} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Link do Produto na Loja (Amazon, Magalu, Mercado Livre, KaBuM, etc.) *
              </label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => handleAutoFillFromUrl(e.target.value)}
                placeholder="Cole o link da Amazon aqui (ex: https://www.amazon.com.br/dp/B0B5PZ4MQ9...)"
                className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-amber-400 transition-colors"
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
                placeholder="Ex: Fire TV Stick HD com Controle Remoto por Voz com Alexa"
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
                  placeholder="Ex: 249.00"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-emerald-500 font-bold text-emerald-400"
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
                  placeholder="Ex: 349.00"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-emerald-500 text-gray-400"
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
                  <option value="Amazon">Amazon Brasil (thiagovinigo-20)</option>
                  <option value="Mercado Livre">Mercado Livre</option>
                  <option value="Magazine Luiza">Magazine Luiza</option>
                  <option value="KaBuM!">KaBuM!</option>
                  <option value="Shopee">Shopee</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Categoria (Nicho)</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs font-semibold focus:outline-none focus:border-emerald-500"
                >
                  <option value="eletronicos">📺 Eletrônicos & Alexa</option>
                  <option value="smartphones">📱 Smartphones & Apple</option>
                  <option value="saude">💊 Saúde & Suplementos (Creatina / Whey)</option>
                  <option value="eletrodomesticos">🍳 Eletrodomésticos & Air Fryer</option>
                  <option value="informatica">💻 Informática & Notebooks</option>
                  <option value="perifericos">🎧 Periféricos & Áudio</option>
                  <option value="games">🎮 Games & Consoles</option>
                  <option value="livros">📚 Livros & Kindle</option>
                  <option value="casa">🏠 Casa & Cozinha</option>
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
                  placeholder="Ex: PRIME20"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-xs focus:outline-none focus:border-emerald-500 uppercase"
                />
              </div>
            </div>

            <div className="space-y-2 pt-1 border-t border-gray-800">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isLightningDeal"
                  checked={isLightningDeal}
                  onChange={(e) => setIsLightningDeal(e.target.checked)}
                  className="w-4 h-4 rounded text-amber-500 bg-gray-900 border-gray-700 focus:ring-amber-500"
                />
                <label htmlFor="isLightningDeal" className="text-xs text-amber-300 font-bold cursor-pointer flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                  Cadastrar como Oferta Relâmpago (destaque na página /ofertas-relampago e selo dourado)
                </label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isFeatured"
                  checked={isFeatured}
                  onChange={(e) => setIsFeatured(e.target.checked)}
                  className="w-4 h-4 rounded text-emerald-600 bg-gray-900 border-gray-700"
                />
                <label htmlFor="isFeatured" className="text-xs text-gray-300 font-semibold cursor-pointer">
                  Destacar no topo da vitrine da página inicial
                </label>
              </div>
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

      {/* ABA 7: STORE HUNTER AI AGENT - CAÇADOR DE LOJAS */}
      {activeTab === "hunter" && (
        <section className="space-y-6">
          {/* Banner do Agente */}
          <div className="relative overflow-hidden rounded-3xl p-6 sm:p-8 border border-violet-500/30 bg-gradient-to-r from-violet-950/60 via-purple-950/30 to-gray-900 shadow-2xl">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div className="max-w-2xl space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/20 border border-violet-500/40 text-violet-300 text-xs font-black uppercase tracking-wider">
                  <Compass className={`w-4 h-4 text-violet-400 ${hunterRunning ? "animate-spin" : ""}`} />
                  Store Hunter AI Agent v1.0 • Radar Autônomo
                </div>
                <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  Agente Caçador de <span className="text-violet-400">Lojas Bem Avaliadas</span>
                </h2>
                <p className="text-sm text-gray-300 leading-relaxed">
                  Nosso agente de inteligência artificial vasculha a internet auditando a reputação de e-commerces brasileiros (selos <strong>RA1000</strong> e <strong>Ótimo</strong> no Reclame Aqui, Ebit, índices de solução) e mapeia programas de afiliados para você expandir o catálogo do Só Promo Boa com 1 clique.
                </p>
                {hunterSuccessMsg && (
                  <div className="p-3 rounded-xl bg-violet-500/20 border border-violet-500/40 text-violet-200 text-xs font-semibold animate-fade-in flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-violet-400 shrink-0" />
                    {hunterSuccessMsg}
                  </div>
                )}
              </div>

              <div className="flex flex-col sm:flex-row lg:flex-col gap-3 shrink-0">
                <button
                  onClick={handleRunHunter}
                  disabled={hunterRunning}
                  className="px-5 py-3 rounded-xl text-xs font-black bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-xl shadow-violet-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Compass className={`w-4 h-4 ${hunterRunning ? "animate-spin" : ""}`} />
                  {hunterRunning ? "Varrendo a Internet..." : "Disparar Varredura do Agente"}
                </button>
                <span className="text-[11px] text-gray-400 text-center">
                  Audita lojas com nota &gt; 8.0 no Reclame Aqui
                </span>
              </div>
            </div>
          </div>

          {/* Cards de Métricas do Hunter */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-card rounded-2xl p-5 border border-gray-800">
              <span className="text-xs font-semibold text-gray-400 block">Total Mapeadas</span>
              <span className="text-2xl font-black text-white">{hunterStats?.total_discovered || 0}</span>
              <span className="text-[10px] text-gray-500 block">lojas auditadas</span>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-amber-500/30 bg-amber-500/5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-amber-300 block">Aguardando Aprovação</span>
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              </div>
              <span className="text-2xl font-black text-amber-400">{hunterStats?.pending_approval || 0}</span>
              <span className="text-[10px] text-amber-300/70 block">prontas para integrar</span>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-emerald-500/30 bg-emerald-500/5">
              <span className="text-xs font-semibold text-emerald-300 block">Lojas Integradas</span>
              <span className="text-2xl font-black text-emerald-400">{hunterStats?.approved || 0}</span>
              <span className="text-[10px] text-emerald-300/70 block">ativas no comparador</span>
            </div>

            <div className="glass-card rounded-2xl p-5 border border-purple-500/30 bg-purple-500/5">
              <span className="text-xs font-semibold text-purple-300 block">Média Reclame Aqui</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <Star className="w-4 h-4 text-purple-400 fill-purple-400" />
                <span className="text-2xl font-black text-purple-300">{hunterStats?.average_reclame_aqui || 0}</span>
                <span className="text-xs text-gray-500">/ 10</span>
              </div>
              <span className="text-[10px] text-purple-300/70 block">padrão de excelência</span>
            </div>
          </div>

          {/* Caixa de Auditoria Instantânea de URL */}
          <div className="glass-card rounded-2xl p-5 border border-gray-800 bg-gray-900/60">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Globe className="w-4 h-4 text-violet-400" />
                  Auditar Qualquer Loja por URL
                </h3>
                <p className="text-xs text-gray-400">
                  Encontrou uma loja e quer que o agente audite a reputação e afiliação dela? Cole a URL abaixo:
                </p>
              </div>
            </div>

            <form onSubmit={handleAuditCustomUrl} className="flex flex-col sm:flex-row gap-2.5">
              <input
                type="text"
                placeholder="Ex: https://www.terabyteshop.com.br ou kabum.com.br"
                value={customAuditUrl}
                onChange={(e) => setCustomAuditUrl(e.target.value)}
                className="flex-1 bg-gray-950 border border-gray-700 rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 transition-colors"
                required
              />
              <input
                type="text"
                placeholder="Nome da Loja (Opcional)"
                value={customAuditName}
                onChange={(e) => setCustomAuditName(e.target.value)}
                className="sm:w-56 bg-gray-950 border border-gray-700 rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 transition-colors"
              />
              <button
                type="submit"
                disabled={auditing}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-violet-600 hover:bg-violet-500 text-white transition-all disabled:opacity-50 shrink-0 flex items-center justify-center gap-2"
              >
                <Compass className={`w-3.5 h-3.5 ${auditing ? "animate-spin" : ""}`} />
                {auditing ? "Auditando..." : "Auditar com IA"}
              </button>
            </form>

            {auditMsg && (
              <p className="mt-2 text-xs font-semibold text-violet-300 animate-fade-in">
                {auditMsg}
              </p>
            )}
          </div>

          {/* Filtros e Busca de Lojas */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
            <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
              <button
                onClick={() => setHunterFilter("pending")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                  hunterFilter === "pending"
                    ? "bg-amber-500 text-gray-950 shadow-md shadow-amber-500/20"
                    : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                Aguardando Aprovação ({hunterStores.filter((s) => s.status === "pending").length})
              </button>

              <button
                onClick={() => setHunterFilter("approved")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                  hunterFilter === "approved"
                    ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/20"
                    : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                Integradas ({hunterStores.filter((s) => s.status === "approved").length})
              </button>

              <button
                onClick={() => setHunterFilter("all")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  hunterFilter === "all"
                    ? "bg-violet-600 text-white shadow-md shadow-violet-600/20"
                    : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                Todas ({hunterStores.length})
              </button>
            </div>

            <div className="relative sm:w-72">
              <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filtrar por nome, nicho..."
                value={hunterSearch}
                onChange={(e) => setHunterSearch(e.target.value)}
                className="w-full bg-gray-950 border border-gray-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
              />
            </div>
          </div>

          {/* Grid de Cards de Lojas Descobertas */}
          {hunterStores.length === 0 ? (
            <div className="glass-card rounded-2xl p-12 text-center border border-gray-800 space-y-3">
              <Compass className="w-12 h-12 text-violet-400/50 mx-auto animate-pulse" />
              <h3 className="text-base font-bold text-white">Nenhuma loja auditada no momento</h3>
              <p className="text-xs text-gray-400 max-w-md mx-auto">
                Clique no botão "Disparar Varredura do Agente" acima para o Store Hunter AI mapear e auditar automaticamente os maiores e-commerces brasileiros.
              </p>
              <button
                onClick={handleRunHunter}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-violet-600 hover:bg-violet-500 text-white transition-all inline-flex items-center gap-2 mt-2"
              >
                <Compass className="w-3.5 h-3.5" /> Iniciar Varredura Agora
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {hunterStores
                .filter((s) => {
                  if (hunterFilter !== "all" && s.status !== hunterFilter) return false;
                  if (hunterSearch) {
                    const q = hunterSearch.toLowerCase();
                    return (
                      s.name.toLowerCase().includes(q) ||
                      s.domain.toLowerCase().includes(q) ||
                      s.category.toLowerCase().includes(q)
                    );
                  }
                  return true;
                })
                .map((store) => {
                  const isPending = store.status === "pending";
                  const isApproved = store.status === "approved";
                  const isRejected = store.status === "rejected";

                  return (
                    <div
                      key={store.id}
                      className={`glass-card rounded-2xl p-5 border transition-all flex flex-col justify-between space-y-4 ${
                        isPending
                          ? "border-amber-500/30 hover:border-amber-500/50 bg-gradient-to-b from-gray-900/90 to-amber-950/10"
                          : isApproved
                          ? "border-emerald-500/30 bg-gradient-to-b from-gray-900/90 to-emerald-950/10"
                          : "border-gray-800 opacity-60"
                      }`}
                    >
                      {/* Topo do Card */}
                      <div>
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-xl bg-gray-800 border border-gray-700 flex items-center justify-center overflow-hidden shrink-0">
                              {store.logo_url ? (
                                <img
                                  src={store.logo_url}
                                  alt={store.name}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <Store className="w-6 h-6 text-violet-400" />
                              )}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h3 className="text-base font-black text-white">{store.name}</h3>
                                <a
                                  href={store.official_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  title="Abrir site oficial"
                                  className="text-gray-400 hover:text-white"
                                >
                                  <ExternalLink className="w-3.5 h-3.5" />
                                </a>
                              </div>
                              <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-[11px] text-gray-400 font-mono">{store.domain}</span>
                                <span className="text-[10px] text-gray-500">•</span>
                                <span className="text-[11px] font-semibold text-violet-300">{store.category}</span>
                              </div>
                            </div>
                          </div>

                          {/* Trust Score */}
                          <div className="text-right shrink-0">
                            <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-black">
                              <ShieldCheck className="w-3.5 h-3.5" />
                              {store.trust_score}% Confiável
                            </div>
                          </div>
                        </div>

                        {/* Métricas Auditadas */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-4 p-3 rounded-xl bg-gray-950/60 border border-gray-800/80 text-xs">
                          <div>
                            <span className="text-[10px] text-gray-400 block font-semibold">Reclame Aqui</span>
                            <div className="flex items-center gap-1 mt-0.5">
                              <span className={`px-1.5 py-0.2 rounded text-[10px] font-black ${
                                store.reclame_aqui_badge === "RA1000"
                                  ? "bg-purple-500 text-white"
                                  : "bg-emerald-500/20 text-emerald-300"
                              }`}>
                                {store.reclame_aqui_badge || "Auditado"}
                              </span>
                              <span className="font-bold text-white">{store.reclame_aqui_score || "-"}</span>
                            </div>
                          </div>

                          <div>
                            <span className="text-[10px] text-gray-400 block font-semibold">Índice Solução</span>
                            <span className="font-bold text-emerald-400 block mt-0.5">
                              {store.reclame_aqui_resolved_rate ? `${store.reclame_aqui_resolved_rate}%` : "90%+"}
                            </span>
                          </div>

                          <div>
                            <span className="text-[10px] text-gray-400 block font-semibold">Rede de Afiliados</span>
                            <span className="font-semibold text-gray-200 block mt-0.5 truncate" title={store.affiliate_network || ""}>
                              {store.affiliate_network || "Direto"}
                            </span>
                          </div>

                          <div>
                            <span className="text-[10px] text-gray-400 block font-semibold">Comissão Estimada</span>
                            <span className="font-black text-emerald-400 block mt-0.5">
                              {store.estimated_commission || "Até 8%"}
                            </span>
                          </div>
                        </div>

                        {/* Justificativa do Agente */}
                        {store.discovered_reason && (
                          <div className="mt-3 p-3 rounded-xl bg-violet-500/5 border border-violet-500/20 text-[11px] text-gray-300 leading-relaxed flex items-start gap-2">
                            <Sparkles className="w-3.5 h-3.5 text-violet-400 shrink-0 mt-0.5" />
                            <span>
                              <strong className="text-violet-300">Análise do Agente:</strong> {store.discovered_reason}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Footer com Ações */}
                      <div className="pt-3 border-t border-gray-800/80 flex items-center justify-between gap-3">
                        {isPending ? (
                          <div className="flex items-center gap-2 w-full">
                            <button
                              onClick={() => handleApproveStore(store.id)}
                              className="flex-1 py-2 rounded-xl text-xs font-black bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-md shadow-emerald-600/20 transition-all flex items-center justify-center gap-1.5"
                            >
                              <CheckCircle2 className="w-4 h-4" />
                              Aprovar e Integrar ao SóPromoBoa
                            </button>
                            <button
                              onClick={() => handleRejectStore(store.id)}
                              className="px-3 py-2 rounded-xl text-xs font-bold bg-gray-800 hover:bg-rose-500/20 text-gray-400 hover:text-rose-400 border border-gray-700 transition-colors"
                              title="Descartar sugestão"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          </div>
                        ) : isApproved ? (
                          <div className="flex items-center justify-between w-full">
                            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                              <CheckCircle2 className="w-4 h-4" /> Integrada ao Catálogo e Comparador
                            </span>
                            <a
                              href={store.official_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                            >
                              Visitar Loja <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between w-full">
                            <span className="text-xs text-gray-500 italic">Sugestão descartada</span>
                            <button
                              onClick={() => handleApproveStore(store.id)}
                              className="text-xs text-violet-400 hover:underline"
                            >
                              Reverter & Integrar
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </section>
      )}

      {/* ABA 8: CADASTRO EM LOJAS DE AFILIADOS (MELHORES PRODUTOS) */}
      {activeTab === "cadastro_afiliados" && (
        <section className="space-y-6">
          {/* Banner Principal */}
          <div className="relative overflow-hidden rounded-3xl p-6 sm:p-8 border border-amber-500/40 bg-gradient-to-r from-amber-950/50 via-orange-950/30 to-gray-900 shadow-2xl">
            <div className="max-w-3xl space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-black uppercase tracking-wider">
                <ShoppingBag className="w-4 h-4 text-amber-400" />
                Central Oficial de Credenciamento
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Cadastre-se nas Melhores <span className="text-amber-400">Lojas de Afiliados</span>
              </h2>
              <p className="text-sm text-gray-300 leading-relaxed">
                Para começar a faturar comissões em cada venda gerada pelo <strong>Só Promo Boa</strong>, cadastre-se nos programas oficiais abaixo. Assim que receber sua aprovação, cole sua <strong>Tag/ID</strong> diretamente no card correspondente para ativar a comissão automática em todos os links da plataforma!
              </p>
            </div>
          </div>

          {/* Grid dos Programas Oficiais */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {[
              {
                slug: "amazon",
                name: "Amazon Brasil Associados",
                headline: "Maior conversão em Tecnologia, iPhones, Echo Alexa e Livros",
                category: "Smartphones, Tech, Casa Inteligente",
                commission: "Até 15% por venda",
                cookie: "24 horas",
                registerUrl: "https://associados.amazon.com.br/",
                bestProducts: ["iPhones & Apple Watch", "Dispositivos Echo com Alexa", "Kindle & Livros", "Periféricos & Hardware Gamer"],
                tips: "Aprovação imediata. Ao se cadastrar, você define seu Store ID (ex: sopromoboa-20).",
                badgeColor: "bg-amber-500/10 text-amber-300 border-amber-500/30",
              },
              {
                slug: "mercadolivre",
                name: "Mercado Livre Afiliados",
                headline: "Maior marketplace do Brasil com entrega Full no mesmo dia",
                category: "Eletrônicos, Monitores, Ferramentas, TVs",
                commission: "Até 16% por venda",
                cookie: "24 horas",
                registerUrl: "https://www.mercadolivre.com.br/afiliados",
                bestProducts: ["Monitores 144Hz/165Hz", "Smart TVs 4K", "Smartphones Samsung e Xiaomi", "Ferramentas & Áudio"],
                tips: "Basta ter uma conta Mercado Livre ativa. Gere links diretos para qualquer anúncio oficial.",
                badgeColor: "bg-yellow-500/10 text-yellow-300 border-yellow-500/30",
              },
              {
                slug: "magalu",
                name: "Parceiro Magalu (Magazine Luiza)",
                headline: "Líder em Eletrodomésticos, Linha Branca, TVs e Celulares",
                category: "Linha Branca, TVs, Eletroportáteis",
                commission: "Até 12% + bônus",
                cookie: "7 dias",
                registerUrl: "https://www.parceiromagalu.com.br/",
                bestProducts: ["Airfryers & Eletroportáteis", "Geladeiras e Máquinas de Lavar", "Smart TVs 50\" e 55\"", "Celulares em promoção Pix"],
                tips: "Você cria sua vitrine 'magazinevoce.com.br/sua_loja' em menos de 5 minutos gratuitamente.",
                badgeColor: "bg-blue-500/10 text-blue-300 border-blue-500/30",
              },
              {
                slug: "shopee",
                name: "Shopee Afiliados",
                headline: "Monetização de alto volume com cupom de frete grátis",
                category: "Acessórios, Gadgets, Periféricos, Moda",
                commission: "Até 14% por venda",
                cookie: "7 dias",
                registerUrl: "https://affiliate.shopee.com.br/",
                bestProducts: ["Fones Bluetooth TWS", "Acessórios e Cabos Gamer", "Achadinhos & Gadgets Úteis", "Monitores e Acessórios de Mesa"],
                tips: "Excelente taxa de conversão em compras impulsivas e cupons agressivos pelo app.",
                badgeColor: "bg-orange-500/10 text-orange-300 border-orange-500/30",
              },
              {
                slug: "awin",
                name: "Awin Brasil (Rede Oficial Dell, Samsung, Electrolux, JBL)",
                headline: "1 único cadastro dá acesso a centenas de lojas oficiais premium",
                category: "Lojas Oficiais das Marcas",
                commission: "4% a 8% por venda",
                cookie: "30 dias",
                registerUrl: "https://www.awin.com/br/afiliados",
                bestProducts: ["Dell (Notebooks e Monitores 4K)", "Samsung Oficial (S24, Galaxy)", "LG Loja Oficial", "Electrolux & JBL Harman"],
                tips: "Rede global de maior ticket médio. Comissões de R$ 150 a R$ 400 por notebook Dell vendido.",
                badgeColor: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
              },
              {
                slug: "lomadee",
                name: "Lomadee / SocialSoul (KaBuM!, Terabyte, Pichau, Fast Shop)",
                headline: "A principal rede brasileira para Hardware, PCs Gamer e Tecnologia",
                category: "Hardware, Games, PCs Completos",
                commission: "3% a 9% por venda",
                cookie: "30 dias",
                registerUrl: "https://www.socialsoul.com.br/",
                bestProducts: ["KaBuM! (Placas RTX, Processadores)", "Terabyteshop (Upgrades Gamer)", "Fast Shop (TVs OLED)", "Loja do Mecânico (Ferramentas)"],
                tips: "Ponto obrigatório para quem monetiza tecnologia e jogos no Brasil. Suporte a deep-link.",
                badgeColor: "bg-purple-500/10 text-purple-300 border-purple-500/30",
              },
              {
                slug: "growth",
                name: "Growth Supplements (Programa Direto)",
                headline: "Maior índice de recompra e retenção do mercado fitness",
                category: "Suplementos & Nutrição Esportiva",
                commission: "5% a 10% de comissão",
                cookie: "30 dias",
                registerUrl: "https://www.gsuplementos.com.br/",
                bestProducts: ["100% Whey Protein Concentrado", "Creatina Monohidratada Creapure", "Multivitamínicos & Ômega 3", "Roupas e Coqueteleiras"],
                tips: "Vencedora RA1000 com nota 9.3. Os clientes compram mensalmente garantindo receita recorrente.",
                badgeColor: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
              },
              {
                slug: "avell",
                name: "Avell Notebooks de Alta Performance",
                headline: "Comissões de até R$ 800 líquidos em uma única venda",
                category: "Laptops para Engenharia, IA e Games",
                commission: "3% a 6% por venda",
                cookie: "30 dias",
                registerUrl: "https://avell.com.br/afiliados",
                bestProducts: ["Workstations Avell A-Series", "Notebooks Gamer com RTX 4080/4090", "Laptops para Arquitetura e Render 3D"],
                tips: "Ticket médio de R$ 9.000 a R$ 18.000. Duas vendas por mês já geram mais de R$ 1.000 de lucro.",
                badgeColor: "bg-rose-500/10 text-rose-300 border-rose-500/30",
              },
            ].map((prog) => {
              const currentTag = programs.find((p) => p.network_slug === prog.slug)?.tracking_id;

              return (
                <div
                  key={prog.slug}
                  className="glass-card rounded-2xl p-6 border border-gray-800 hover:border-amber-500/40 transition-all flex flex-col justify-between space-y-4 bg-gradient-to-b from-gray-900/90 to-gray-950"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${prog.badgeColor}`}>
                          {prog.category}
                        </span>
                        <h3 className="text-lg font-black text-white mt-1.5">{prog.name}</h3>
                        <p className="text-xs text-gray-400 mt-0.5">{prog.headline}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-xs font-black text-emerald-400 px-2.5 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/20 block">
                          {prog.commission}
                        </span>
                        <span className="text-[10px] text-gray-500 block mt-1">Cookie: {prog.cookie}</span>
                      </div>
                    </div>

                    {/* Melhores Produtos para Promover */}
                    <div className="p-3 rounded-xl bg-gray-950 border border-gray-800/80 space-y-1.5">
                      <span className="text-[10px] uppercase font-bold text-gray-400 block tracking-wider">
                        ⭐ Melhores Produtos para Promover:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {prog.bestProducts.map((p, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded-md bg-gray-800 text-[11px] text-gray-300 font-medium"
                          >
                            {p}
                          </span>
                        ))}
                      </div>
                    </div>

                    <p className="text-xs text-amber-300/80 bg-amber-500/5 border border-amber-500/20 p-2.5 rounded-xl">
                      💡 <strong>Dica de aprovação:</strong> {prog.tips}
                    </p>
                  </div>

                  {/* Ações: Cadastrar + Salvar Tag */}
                  <div className="pt-3 border-t border-gray-800/80 space-y-3">
                    <div className="flex items-center gap-2">
                      <a
                        href={prog.registerUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 py-2.5 px-4 rounded-xl text-xs font-black bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-gray-950 shadow-md shadow-amber-500/20 transition-all flex items-center justify-center gap-1.5"
                      >
                        Cadastrar-se Agora na Loja <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>

                    {/* Formulário Rápido de Inserção de Tag */}
                    <div className="p-2.5 rounded-xl bg-gray-950 border border-gray-800 space-y-1.5">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-gray-400 font-semibold">Sua Tag / ID de Afiliado nesta Loja:</span>
                        {currentTag && (
                          <span className="text-emerald-400 font-bold font-mono">
                            Ativa: {currentTag}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          placeholder={currentTag ? `Atualizar tag (${currentTag})` : "Cole sua Tag/ID (ex: seuid-20)"}
                          value={quickTags[prog.slug] || ""}
                          onChange={(e) =>
                            setQuickTags({ ...quickTags, [prog.slug]: e.target.value })
                          }
                          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 font-mono"
                        />
                        <button
                          onClick={() => handleSaveQuickTag(prog.slug, prog.name, prog.commission)}
                          disabled={!quickTags[prog.slug]}
                          className="px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-40 transition-colors shrink-0"
                        >
                          Salvar Tag
                        </button>
                      </div>
                      {quickSavedSlug === prog.slug && (
                        <span className="text-[10px] text-emerald-400 font-semibold block animate-fade-in">
                          ✓ Tag salva com sucesso! Links comissionados ativados.
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
