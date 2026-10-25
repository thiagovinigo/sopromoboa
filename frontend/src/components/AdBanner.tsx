"use client";

import React, { useEffect, useState } from "react";

interface AdBannerProps {
  slotId?: string;
  clientId?: string;
  format?: "auto" | "horizontal" | "rectangle";
  className?: string;
}

export default function AdBanner({
  slotId,
  clientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID || "ca-pub-8215576310884543",
  format = "auto",
  className = "",
}: AdBannerProps) {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (clientId && slotId && typeof window !== "undefined") {
      try {
        // @ts-expect-error - adsbygoogle is dynamically loaded by Google script
        (window.adsbygoogle = window.adsbygoogle || []).push({});
        setIsLoaded(true);
      } catch (err) {
        console.warn("[AdSense] Falha ao renderizar bloco de anúncio:", err);
      }
    }
  }, [clientId, slotId]);

  // Se o cliente AdSense estiver configurado com Slot válido
  if (clientId && slotId) {
    return (
      <div className={`w-full overflow-hidden my-4 text-center ${className}`}>
        <span className="block text-[10px] uppercase font-bold text-gray-500 tracking-wider mb-1">
          Publicidade
        </span>
        <ins
          className="adsbygoogle block"
          style={{ display: "block" }}
          data-ad-client={clientId}
          data-ad-slot={slotId}
          data-ad-format={format}
          data-full-width-responsive="true"
        />
      </div>
    );
  }

  // Placeholder elegante de pré-visualização (visível até você colar o seu pub-ID)
  return (
    <div
      className={`w-full max-w-4xl mx-auto my-6 p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] text-center flex flex-col items-center justify-center gap-1.5 transition-all ${className}`}
    >
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">
          Espaço Reservado • Google AdSense
        </span>
      </div>
      <p className="text-[10px] text-gray-400">
        Pronto para veicular anúncios automáticos e faturar em dólar assim que o domínio for aprovado.
      </p>
    </div>
  );
}
