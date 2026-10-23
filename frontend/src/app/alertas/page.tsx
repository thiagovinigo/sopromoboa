"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AlertasRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/busca-personalizada");
  }, [router]);

  return (
    <div className="py-20 text-center space-y-3">
      <div className="text-sm font-bold text-cyan-400">
        Redirecionando para a nova Busca Personalizada dos Workers...
      </div>
    </div>
  );
}
