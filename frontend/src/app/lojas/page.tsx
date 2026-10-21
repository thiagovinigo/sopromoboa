"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Store,
  ExternalLink,
  ShieldCheck,
  Flame,
  Sparkles,
  ShoppingBag,
  ArrowRight,
  TrendingDown,
  CheckCircle2,
} from "lucide-react";
import { fetchStores, StoreItem } from "@/lib/api";

const STORE_METADATA: Record<
  string,
  {
    description: string;
    highlights: string[];
    officialUrl: string;
    bgGradient: string;
    badgeColor: string;
    borderColor: string;
  }
> = {
  amazon: {
    description:
      "Líder global com entrega rápida Prime, catálogo completo de eletrônicos, Kindles, informática e importados.",
    highlights: ["Frete Grátis com Prime", "Ofertas Relâmpago Diárias", "Garantia A a Z"],
    officialUrl: "https://www.amazon.com.br?tag=sopromoboa-20&utm_source=sopromoboa",
    bgGradient: "from-amber-950/30 to-gray-900/90",
    badgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    borderColor: "hover:border-amber-500/40",
  },
  mercadolivre: {
    description:
      "O maior marketplace da América Latina. Lojas oficiais, entrega Full no mesmo dia e cupons de desconto.",
    highlights: ["Entrega FULL Rápida", "Programa Compra Garantida", "Cupons Diários de Desconto"],
    officialUrl: "https://www.mercadolivre.com.br?matt_tool=sopromoboa&utm_source=sopromoboa",
    bgGradient: "from-yellow-950/30 to-gray-900/90",
    badgeColor: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
    borderColor: "hover:border-yellow-500/40",
  },
  magazineluiza: {
    description:
      "Gigante varejista nacional com fortes ofertas em eletrodomésticos, TVs, celulares e retirada rápida em loja.",
    highlights: ["Retira Rápido em Loja", "Descontos no Pix", "Linha Branca & TV"],
    officialUrl: "https://www.magazineluiza.com.br?utm_source=sopromoboa&utm_medium=afiliado",
    bgGradient: "from-blue-950/30 to-gray-900/90",
    badgeColor: "text-blue-400 bg-blue-500/10 border-blue-500/30",
    borderColor: "hover:border-blue-500/40",
  },
  kabum: {
    description:
      "Maior e-commerce de tecnologia, hardware e games do Brasil. Hardware topo de linha e periféricos gamers.",
    highlights: ["Especialista em Hardware", "Monitores e PCs Gamer", "Atendimento Técnico"],
    officialUrl: "https://www.kabum.com.br?tag=sopromoboa",
    bgGradient: "from-orange-950/30 to-gray-900/90",
    badgeColor: "text-orange-400 bg-orange-500/10 border-orange-500/30",
    borderColor: "hover:border-orange-500/40",
  },
  shopee: {
    description:
      "Marketplace com cupons de frete grátis sem valor mínimo, grandes marcas oficiais e ofertas relâmpago.",
    highlights: ["Cupons de Frete Grátis", "Shopee Oficial Grandes Marcas", "Moedas de Desconto"],
    officialUrl: "https://shopee.com.br?utm_source=sopromoboa",
    bgGradient: "from-rose-950/30 to-gray-900/90",
    badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    borderColor: "hover:border-rose-500/40",
  },
};

export default function LojasPage() {
  const [stores, setStores] = useState<StoreItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8">
      {/* Header da Página de Lojas */}
      <section className="relative overflow-hidden rounded-3xl p-8 sm:p-12 border border-gray-800 bg-gradient-to-r from-blue-950/30 via-gray-900/80 to-gray-900 shadow-2xl">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold uppercase tracking-wider">
            <Store className="w-4 h-4 text-blue-400" />
            Lojas Parceiras & Oficiais
          </div>
          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
            Lojas Monitoradas com <br />
            <span className="text-blue-400">Garantia e Procedência</span>
          </h1>
          <p className="text-sm sm:text-base text-gray-300">
            Nossos workers varrem de forma automatizada e constante as principais plataformas de comércio eletrônico do Brasil. Catalogamos apenas lojas oficiais com emissão de nota fiscal e histórico auditado.
          </p>
        </div>
      </section>

      {/* Grade de Lojas */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-blue-400" />
            Lojas Ativas no Radar
            <span className="text-xs font-normal text-gray-400">({stores.length} lojas integradas)</span>
          </h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="glass-card rounded-3xl h-64 animate-pulse bg-gray-800/40" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stores.map((store) => {
              const meta = STORE_METADATA[store.slug] || {
                description: "Loja oficial monitorada no radar de promoções.",
                highlights: ["Compra Segura", "Nota Fiscal", "Garantia"],
                officialUrl: "https://sopromoboa.com.br",
                bgGradient: "from-gray-900 to-gray-950",
                badgeColor: "text-gray-300 bg-gray-800 border-gray-700",
                borderColor: "hover:border-gray-700",
              };

              return (
                <div
                  key={store.slug}
                  className={`glass-card rounded-3xl p-6 border border-gray-800/90 ${meta.borderColor} bg-gradient-to-b ${meta.bgGradient} transition-all duration-300 flex flex-col justify-between group hover:shadow-xl`}
                >
                  <div className="space-y-4">
                    {/* Topo do card */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-gray-900 border border-gray-800 flex items-center justify-center text-white font-black text-lg group-hover:scale-105 transition-transform shadow-md">
                          <Store className="w-6 h-6 text-blue-400" />
                        </div>
                        <div>
                          <h3 className="font-extrabold text-white text-lg tracking-tight group-hover:text-blue-400 transition-colors">
                            {store.name}
                          </h3>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${meta.badgeColor}`}>
                            {store.affiliate_network || "Loja Oficial"}
                          </span>
                        </div>
                      </div>

                      <div className="text-right">
                        <span className="text-xl font-black text-white block">
                          {store.total_deals}
                        </span>
                        <span className="text-[10px] uppercase font-semibold text-gray-400 tracking-wider">
                          ofertas ativas
                        </span>
                      </div>
                    </div>

                    {/* Descrição */}
                    <p className="text-xs text-gray-300 leading-relaxed">
                      {meta.description}
                    </p>

                    {/* Diferenciais */}
                    <div className="space-y-1.5 pt-2 border-t border-gray-800/60">
                      {meta.highlights.map((h, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-[11px] text-gray-400">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                          <span>{h}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Ações */}
                  <div className="pt-6 grid grid-cols-2 gap-2 border-t border-gray-800/80 mt-5">
                    <Link
                      href={`/?source=${encodeURIComponent(store.name)}`}
                      className="px-3 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 hover:text-white text-xs font-bold text-center transition-all flex items-center justify-center gap-1.5"
                    >
                      Ver Ofertas <ArrowRight className="w-3.5 h-3.5 text-rose-500" />
                    </Link>

                    <a
                      href={meta.officialUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-600 text-white text-xs font-bold text-center shadow-md shadow-blue-600/20 transition-all flex items-center justify-center gap-1.5"
                    >
                      Ir à Loja <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Faixa Informativa de Garantia e Compliance */}
      <section className="glass-card rounded-2xl p-6 border border-gray-800 bg-gray-900/60 text-xs text-gray-400 space-y-2">
        <div className="flex items-center gap-2 text-white font-bold text-sm">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Transparência & Links Comissionados
        </div>
        <p>
          O Só Promo Boa é uma plataforma independente de agregação e auditoria de promoções. Todos os links de lojas parceiras contêm parâmetros oficiais de rastreamento dos programas de afiliados (Amazon Associates, Parceiro Magalu, Mercado Livre Afiliados, KaBuM! Afiliados). Isso garante que o usuário receba o desconto original e suporte o projeto sem nenhum custo adicional na compra.
        </p>
      </section>
    </div>
  );
}
