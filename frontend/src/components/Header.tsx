"use client";

import React from "react";
import Link from "next/link";
import { Flame, Sparkles, Store, Bot, Zap } from "lucide-react";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-[#080c14]/85 backdrop-blur-md border-b border-white/[0.06]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl flame-gradient flex items-center justify-center text-white shadow-md shadow-rose-500/20 group-hover:scale-105 transition-transform">
              <Flame className="w-5 h-5" />
            </div>
            <div>
              <span className="text-lg font-black tracking-tight text-white flex items-center gap-1">
                QUE<span className="text-rose-500">PROMO</span>
              </span>
              <span className="text-[9px] uppercase font-bold tracking-widest text-gray-400 block -mt-1">
                Ofertas & Menores Preços
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1.5">
            <Link
              href="/ofertas-relampago"
              className="text-xs font-bold text-amber-300 hover:text-amber-200 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 px-3.5 py-1.5 rounded-xl transition-all flex items-center gap-1.5 shadow-sm shadow-amber-500/10"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
              Ofertas Relâmpago
            </Link>
            <Link
              href="/"
              className="text-xs font-semibold text-gray-300 hover:text-white hover:bg-white/[0.05] px-3 py-1.5 rounded-xl transition-all flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-gray-400" />
              Todas as Ofertas
            </Link>
            <Link
              href="/radar"
              className="text-xs font-semibold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 px-3 py-1.5 rounded-xl transition-all flex items-center gap-1.5"
            >
              <Flame className="w-3.5 h-3.5 text-rose-500" />
              Radar de Quedas
            </Link>
            <Link
              href="/busca-personalizada"
              className="text-xs font-semibold text-gray-300 hover:text-white hover:bg-white/[0.05] px-3.5 py-1.5 rounded-xl transition-all flex items-center gap-1.5"
            >
              <Bot className="w-3.5 h-3.5 text-cyan-400" />
              Busca Personalizada
            </Link>
            <Link
              href="/lojas"
              className="text-xs font-semibold text-gray-300 hover:text-white hover:bg-white/[0.05] px-3.5 py-1.5 rounded-xl transition-all flex items-center gap-1.5"
            >
              <Store className="w-3.5 h-3.5 text-blue-400" />
              Lojas Parceiras
            </Link>
            <Link
              href="/favoritos"
              className="text-xs font-semibold text-gray-300 hover:text-white hover:bg-white/[0.05] px-3.5 py-1.5 rounded-xl transition-all flex items-center gap-1.5"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="w-3.5 h-3.5 text-rose-500"
              >
                <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              </svg>
              Favoritos
            </Link>
          </nav>

        </div>
      </div>
    </header>
  );
}
