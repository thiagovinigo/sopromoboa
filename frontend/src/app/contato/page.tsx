import type { Metadata } from "next";
import Link from "next/link";
import { Mail, MessageCircle, HelpCircle, ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Contato | Que Promo",
  description: "Fale com a equipe do Que Promo. Dúvidas, parcerias, relatórios de preços e imprensa.",
};

export default function ContatoPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8 py-6 text-gray-300">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Voltar para as ofertas
      </Link>

      <div className="border-b border-white/[0.08] pb-6">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Fale Conosco</h1>
        <p className="text-sm text-gray-400 mt-2">
          Estamos prontos para atender você, lojistas parceiros e membros da comunidade.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.08] space-y-3">
          <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <Mail className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-white text-base">E-mail Oficial</h3>
          <p className="text-xs text-gray-400">
            Dúvidas gerais, suporte a alertas de preço, sugestões de lojas ou parcerias comerciais:
          </p>
          <a
            href="mailto:contato@quepromo.com.br"
            className="inline-block text-sm font-bold text-rose-400 hover:text-rose-300 transition-colors"
          >
            contato@quepromo.com.br
          </a>
        </div>

        <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/[0.08] space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <MessageCircle className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-white text-base">Comunidade & Redes</h3>
          <p className="text-xs text-gray-400">
            Acompanhe nossas atualizações em tempo real e relatórios de promoções:
          </p>
          <span className="inline-block text-sm font-semibold text-gray-300">
            @quepromo.com.br
          </span>
        </div>
      </div>

      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border border-blue-500/20 space-y-2">
        <div className="flex items-center gap-2 text-blue-400 text-sm font-bold">
          <HelpCircle className="w-4 h-4" />
          <span>Viu uma divergência de preço em alguma loja?</span>
        </div>
        <p className="text-xs text-gray-400 leading-relaxed">
          Nossos robôs atualizam os dados a cada hora. Se uma oferta esgotou ou mudou de preço antes do próximo ciclo, você pode reportar enviando o link para <strong className="text-white">contato@quepromo.com.br</strong> e nosso sistema revalida imediatamente.
        </p>
      </div>
    </div>
  );
}
