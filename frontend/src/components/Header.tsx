"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Flame, Bell, Link2, Sparkles, RefreshCw, Search, Store, Bot } from "lucide-react";
import { triggerWorker } from "@/lib/api";

export default function Header() {
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState("");

  const handleSync = async () => {
    setSyncing(true);
    setSyncMsg("Atualizando promoções...");
    try {
      await triggerWorker();
      setSyncMsg("Worker em execução!");
      setTimeout(() => setSyncMsg(""), 4000);
    } catch {
      setSyncMsg("Erro ao acionar");
      setTimeout(() => setSyncMsg(""), 3000);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-[#0b0f19]/90 backdrop-blur-md border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl flame-gradient flex items-center justify-center text-white shadow-lg shadow-rose-500/20 group-hover:scale-105 transition-transform">
              <Flame className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <span className="text-xl font-black tracking-tight text-white flex items-center gap-1">
                SÓ PROMO <span className="text-rose-500">BOA</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest text-gray-400 block -mt-1">
                Radar de Quedas de Preço
              </span>
            </div>
          </Link>

          {/* Navigation Links - Momento 1: Usuário Final */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/"
              className="text-sm font-semibold text-gray-300 hover:text-white transition-colors flex items-center gap-1.5"
            >
              <Sparkles className="w-4 h-4 text-rose-500" />
              Ofertas
            </Link>
            <Link
              href="/radar"
              className="text-sm font-semibold text-rose-400 hover:text-rose-300 transition-colors flex items-center gap-1.5 bg-rose-500/10 px-3 py-1 rounded-full border border-rose-500/20"
            >
              <Flame className="w-4 h-4 text-rose-500" />
              Radar de Quedas
            </Link>
            <Link
              href="/favoritos"
              className="text-sm font-semibold text-rose-300 hover:text-white transition-colors flex items-center gap-1.5"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="w-4 h-4 text-rose-500"
              >
                <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              </svg>
              Favoritos
            </Link>
            <Link
              href="/busca-personalizada"
              className="text-sm font-semibold text-gray-300 hover:text-white transition-colors flex items-center gap-1.5"
            >
              <Bot className="w-4 h-4 text-cyan-400" />
              Busca Personalizada
            </Link>
            <Link
              href="/lojas"
              className="text-sm font-semibold text-gray-300 hover:text-white transition-colors flex items-center gap-1.5"
            >
              <Store className="w-4 h-4 text-blue-400" />
              Lojas
            </Link>
          </nav>

          {/* Action buttons - Momento 2: Administrador & Monetização */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleSync}
              disabled={syncing}
              title="Executar varredura dos scrapers"
              className="hidden sm:flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin text-rose-500" : ""}`} />
              {syncMsg || "Atualizar Ofertas"}
            </button>

            <Link
              href="/admin"
              className="text-xs font-black px-3.5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-1.5"
            >
              <Link2 className="w-3.5 h-3.5" />
              Painel Admin (Afiliados)
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
