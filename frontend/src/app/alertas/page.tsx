"use client";

import React, { useState, useEffect } from "react";
import {
  Bell,
  Trash2,
  Plus,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Sparkles,
} from "lucide-react";
import { fetchMyAlerts, deleteAlert } from "@/lib/alerts";
import AlertModal from "@/components/AlertModal";

interface UserAlert {
  id: number;
  search_term: string;
  target_price?: number | null;
  min_discount_percent?: number | null;
  category?: string | null;
  is_active: number;
  matched_count: number;
  created_at: string;
}

export default function MyAlertsPage() {
  const [alerts, setAlerts] = useState<UserAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = () => {
    fetchMyAlerts().then((res) => {
      setAlerts(res);
      setLoading(false);
    });
  };

  const handleDelete = async (id: number) => {
    await deleteAlert(id);
    loadAlerts();
  };

  const formatBRL = (val?: number | null) => {
    if (!val) return "Qualquer valor";
    return val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="relative overflow-hidden rounded-3xl p-8 border border-amber-500/30 bg-gradient-to-r from-amber-950/40 via-gray-900/80 to-gray-900/90 shadow-2xl">
        <div className="max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-black uppercase tracking-wider">
            <Bell className="w-4 h-4 text-amber-400" />
            Central de Monitoramento
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Meus Alertas de <br />
            <span className="text-amber-400">Queda de Preço</span>
          </h1>
          <p className="text-sm text-gray-300">
            Gerencie os produtos e termos que você está monitorando. Sempre que um item atingir o seu preço-alvo ou percentual de desconto nas varreduras dos workers, o radar sinaliza para você.
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-amber-400" />
          Alertas Ativos ({alerts.length})
        </h2>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-amber-600 hover:bg-amber-500 transition-colors flex items-center gap-1.5 shadow-md shadow-amber-600/20"
        >
          <Plus className="w-4 h-4" /> Novo Alerta
        </button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="glass-card rounded-2xl h-24 animate-pulse bg-gray-800/40" />
          ))}
        </div>
      ) : alerts.length === 0 ? (
        <div className="glass-card rounded-3xl p-12 text-center space-y-4">
          <Bell className="w-12 h-12 text-gray-600 mx-auto" />
          <h3 className="font-bold text-white text-lg">Nenhum alerta configurado ainda</h3>
          <p className="text-xs text-gray-400 max-w-sm mx-auto">
            Ao navegar pelas ofertas, clique no ícone de sino nos cards ou crie um alerta personalizado com seu termo de interesse.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-600 shadow-md shadow-rose-600/20"
          >
            Criar Meu Primeiro Alerta
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="glass-card rounded-2xl p-5 border border-gray-800 flex items-start justify-between gap-4"
            >
              <div className="space-y-2">
                <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-md uppercase">
                  {alert.category || "Geral"}
                </span>
                <h3 className="font-bold text-base text-white">{alert.search_term}</h3>
                <div className="text-xs text-gray-400 space-y-1">
                  <div>
                    Alvo Máximo: <strong className="text-white">{formatBRL(alert.target_price)}</strong>
                  </div>
                  {alert.min_discount_percent && (
                    <div>
                      Desconto Mínimo: <strong className="text-emerald-400">{alert.min_discount_percent}% OFF</strong>
                    </div>
                  )}
                  {alert.matched_count > 0 && (
                    <div className="text-emerald-400 font-bold flex items-center gap-1 pt-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {alert.matched_count} oferta(s) identificada(s)
                    </div>
                  )}
                </div>
              </div>

              <button
                onClick={() => handleDelete(alert.id)}
                title="Excluir alerta"
                className="p-2 rounded-xl bg-gray-800 hover:bg-rose-500/20 text-gray-400 hover:text-rose-400 border border-gray-700 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Informações de Privacidade */}
      <section className="glass-card rounded-3xl p-6 border border-gray-800 text-xs text-gray-400 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="text-white block mb-1">Como seus alertas são protegidos:</strong>
          Seus alertas estão vinculados exclusivamente a um token criptográfico anônimo salvo na memória do seu navegador (<code className="text-amber-400">localStorage</code>). Nenhuma informação pessoal ou e-mail é armazenada desnecessariamente.
        </div>
      </section>

      {/* Modal */}
      <AlertModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          loadAlerts();
        }}
      />
    </div>
  );
}
