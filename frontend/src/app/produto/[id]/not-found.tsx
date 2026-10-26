import Link from "next/link";
import { ChevronLeft, Flame } from "lucide-react";

export default function ProductNotFound() {
  return (
    <div className="glass-card rounded-3xl p-12 text-center space-y-4">
      <Flame className="w-12 h-12 text-rose-500 mx-auto" />
      <h1 className="text-xl font-bold text-white">Oferta não encontrada ou esgotada</h1>
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gray-800 text-gray-300 hover:text-white text-xs font-semibold"
      >
        <ChevronLeft className="w-4 h-4" /> Voltar para a página inicial
      </Link>
    </div>
  );
}
