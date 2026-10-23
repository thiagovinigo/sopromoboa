"use client";

import React, { useState } from "react";
import { X, Bell, CheckCircle2, ShieldCheck, Tag } from "lucide-react";
import { Deal } from "@/lib/api";
import { createAlert } from "@/lib/alerts";

interface AlertModalProps {
  deal?: Deal | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function AlertModal({ deal, isOpen, onClose }: AlertModalProps) {
  const [searchTerm, setSearchTerm] = useState(deal?.title || "");
  const [targetPrice, setTargetPrice] = useState<string>(
    deal ? (deal.price * 0.9).toFixed(2) : ""
  );
  const [minDiscount, setMinDiscount] = useState<string>("15");
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  // Sincroniza se o deal mudar
  React.useEffect(() => {
    if (deal) {
      setSearchTerm(deal.title);
      setTargetPrice((deal.price * 0.9).toFixed(2));
    }
  }, [deal]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setSaving(true);
    try {
      await createAlert({
        search_term: searchTerm.trim(),
        target_price: targetPrice ? parseFloat(targetPrice) : undefined,
        min_discount_percent: minDiscount ? parseFloat(minDiscount) : undefined,
        category: deal?.category,
      });
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 2000);
    } catch (err) {
      console.error("Erro ao salvar alerta:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="glass-card bg-[#111827] border border-gray-700 rounded-3xl max-w-md w-full p-6 shadow-2xl relative overflow-hidden">
        {/* Glow de fundo */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Alerta de Queda de Preço</h3>
              <p className="text-xs text-gray-400">Receba aviso quando o valor atingir seu alvo</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {success ? (
          <div className="py-8 text-center space-y-3">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto animate-bounce" />
            <h4 className="font-bold text-white text-lg">Alerta Ativado com Sucesso!</h4>
            <p className="text-xs text-gray-400 max-w-xs mx-auto">
              O radar do Que Promo monitorará novas varreduras e sinalizará as promoções que atingirem sua meta.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Termo de busca / Nome do produto
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Ex: iPhone 15, PlayStation 5, Air Fryer..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-rose-500 transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">
                  Preço Alvo Máximo (R$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  placeholder="Ex: 3500.00"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-rose-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">
                  Desconto Mínimo (%)
                </label>
                <input
                  type="number"
                  value={minDiscount}
                  onChange={(e) => setMinDiscount(e.target.value)}
                  placeholder="Ex: 20"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-rose-500 transition-colors"
                />
              </div>
            </div>

            <div className="p-3 rounded-xl bg-gray-900/60 border border-gray-800 text-[11px] text-gray-400 flex items-start gap-2">
              <ShieldCheck className="w-4 h-4 text-rose-500 flex-shrink-0 mt-0.5" />
              <span>
                <strong>100% Privado e Seguro:</strong> Não exigimos cadastro de e-mail ou telefone. Seu alerta fica salvo no token anônimo do seu próprio navegador.
              </span>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-semibold text-gray-300 hover:text-white rounded-xl bg-gray-800 hover:bg-gray-700 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-5 py-2 text-xs font-bold text-white rounded-xl bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-600 shadow-md shadow-rose-600/30 transition-all disabled:opacity-50"
              >
                {saving ? "Salvando..." : "Criar Alerta"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
