"use client";

import React, { useState } from "react";
import { PriceHistoryPoint } from "@/lib/api";
import { TrendingDown, Calendar, ShieldCheck } from "lucide-react";

interface PriceChartProps {
  history: PriceHistoryPoint[];
  currentPrice: number;
  lowestPrice?: number | null;
}

export default function PriceChart({ history, currentPrice, lowestPrice }: PriceChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (!history || history.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-6 text-center text-gray-400 text-sm">
        Primeira aferição de preço registrada hoje. O histórico acumulará novas variações a cada varredura.
      </div>
    );
  }

  // Ordena por data
  const sorted = [...history].sort(
    (a, b) => new Date(a.seen_at).getTime() - new Date(b.seen_at).getTime()
  );

  // Calcula limites
  const prices = sorted.map((h) => h.price);
  const minP = Math.min(...prices, currentPrice);
  const maxP = Math.max(...prices, currentPrice);
  const range = maxP - minP === 0 ? 1 : maxP - minP;

  // Dimensões SVG
  const width = 600;
  const height = 180;
  const paddingX = 40;
  const paddingY = 25;
  const plotWidth = width - paddingX * 2;
  const plotHeight = height - paddingY * 2;

  const points = sorted.map((h, i) => {
    const x =
      sorted.length === 1
        ? width / 2
        : paddingX + (i / (sorted.length - 1)) * plotWidth;
    const y =
      height - paddingY - ((h.price - minP) / range) * plotHeight;
    return { x, y, price: h.price, date: h.seen_at };
  });

  const pathD =
    points.length === 1
      ? `M ${points[0].x - 40} ${points[0].y} L ${points[0].x + 40} ${points[0].y}`
      : points.reduce(
          (acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`),
          ""
        );

  const formatBRL = (val: number) =>
    val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const formatDate = (iso: string) => {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
    } catch {
      return "";
    }
  };

  return (
    <div className="glass-card rounded-2xl p-6 relative">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <h4 className="text-base font-bold text-white flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-rose-500" />
            Evolução Histórica do Preço
          </h4>
          <p className="text-xs text-gray-400">
            Aferição contínua para comprovar se a promoção é real ou 'pela metade do dobro'.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-xl">
            <span className="text-[10px] uppercase font-bold text-emerald-400 block">Menor Histórico</span>
            <span className="text-sm font-black text-emerald-300">
              {formatBRL(lowestPrice || minP)}
            </span>
          </div>
          <div className="bg-gray-800/80 border border-gray-700 px-3 py-1.5 rounded-xl">
            <span className="text-[10px] uppercase font-bold text-gray-400 block">Preço Atual</span>
            <span className="text-sm font-black text-white">
              {formatBRL(currentPrice)}
            </span>
          </div>
        </div>
      </div>

      {/* Gráfico SVG */}
      <div className="w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-44 overflow-visible"
        >
          {/* Linhas de grade sutis */}
          <line
            x1={paddingX}
            y1={paddingY}
            x2={width - paddingX}
            y2={paddingY}
            stroke="#334155"
            strokeDasharray="4 4"
            strokeOpacity="0.4"
          />
          <line
            x1={paddingX}
            y1={height - paddingY}
            x2={width - paddingX}
            y2={height - paddingY}
            stroke="#334155"
            strokeDasharray="4 4"
            strokeOpacity="0.4"
          />

          {/* Área sombreada */}
          {points.length > 1 && (
            <path
              d={`${pathD} L ${points[points.length - 1].x} ${height - paddingY} L ${points[0].x} ${height - paddingY} Z`}
              fill="url(#priceGradient)"
              opacity="0.25"
            />
          )}

          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" />
              <stop offset="100%" stopColor="#1e1b4b" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Linha principal de preço */}
          <path
            d={pathD}
            fill="none"
            stroke="#f43f5e"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Pontos de aferição */}
          {points.map((p, i) => (
            <g key={i}>
              <circle
                cx={p.x}
                cy={p.y}
                r={hoveredIndex === i ? 6 : 4}
                className="fill-rose-500 stroke-white stroke-2 cursor-pointer transition-all"
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              />
              <text
                x={p.x}
                y={height - 6}
                textAnchor="middle"
                fontSize="10"
                fill="#94a3b8"
                className="select-none font-medium"
              >
                {formatDate(p.date)}
              </text>
            </g>
          ))}
        </svg>
      </div>

      {/* Tooltip de detalhe */}
      {hoveredIndex !== null && points[hoveredIndex] && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-gray-900 border border-rose-500/50 px-3 py-1.5 rounded-xl shadow-xl text-xs z-20 pointer-events-none">
          <span className="font-bold text-white block">
            {formatBRL(points[hoveredIndex].price)}
          </span>
          <span className="text-[10px] text-gray-400 flex items-center gap-1 mt-0.5">
            <Calendar className="w-3 h-3" />
            {new Date(points[hoveredIndex].date).toLocaleString("pt-BR")}
          </span>
        </div>
      )}

      <div className="mt-3 flex items-center gap-2 text-xs text-gray-400 bg-gray-900/50 p-2.5 rounded-xl border border-gray-800">
        <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
        <span>
          O Só Promo Boa verifica e congela o histórico a cada alteração para garantir que promoções como 'Metade do Dobro' não enganem os usuários.
        </span>
      </div>
    </div>
  );
}
