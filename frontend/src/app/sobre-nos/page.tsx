import type { Metadata } from "next";
import Link from "next/link";
import { Flame, ShieldCheck, Zap, Bot, ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Sobre Nós | Que Promo",
  description: "Conheça o Que Promo, a plataforma de monitoramento e auditoria de preços reais do e-commerce brasileiro.",
};

export default function SobreNosPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6 text-gray-300">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Voltar para as ofertas
      </Link>

      <div className="border-b border-white/[0.08] pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold mb-3">
          <Flame className="w-3.5 h-3.5" />
          <span>Nossa Missão</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Sobre o Que Promo</h1>
        <p className="text-sm text-gray-400 mt-2">
          Tecnologia para você nunca mais cair em falsas promoções da internet.
        </p>
      </div>

      <div className="space-y-6 text-sm leading-relaxed">
        <section className="space-y-3">
          <p>
            O <strong>Que Promo</strong> nasceu com uma missão clara: <strong>auditar preços reais</strong> e dar aos consumidores brasileiros 
            uma ferramenta transparente para separar promoções verdadeiras de maquiagens de preço ("metade do dobro").
          </p>
          <p>
            Diariamente, nossos robôs analisam centenas de milhares de produtos nos maiores e-commerces do Brasil — incluindo 
            <strong> Amazon, Mercado Livre, Shopee e Magazine Luiza</strong>. A cada variação, nosso motor verifica o histórico de preço, 
            isola apenas as quedas reais e calcula se aquele valor está de fato no menor nível dos últimos meses.
          </p>
        </section>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
          <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06] space-y-2">
            <Bot className="w-6 h-6 text-cyan-400" />
            <h3 className="font-bold text-white text-base">Robôs Autônomos</h3>
            <p className="text-xs text-gray-400">Varredura contínua de hora em hora buscando novas ofertas e expurgando produtos esgotados.</p>
          </div>

          <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06] space-y-2">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            <h3 className="font-bold text-white text-base">Auditoria Histórica</h3>
            <p className="text-xs text-gray-400">Identificação clara do menor preço apurado para você comprar apenas no momento certo.</p>
          </div>

          <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06] space-y-2">
            <Zap className="w-6 h-6 text-amber-400" />
            <h3 className="font-bold text-white text-base">Ofertas Relâmpago</h3>
            <p className="text-xs text-gray-400">Vitrine dedicada com descontos a partir de 25% verificados em itens de alta demanda.</p>
          </div>
        </div>

        <section className="space-y-3 pt-4">
          <h2 className="text-lg font-bold text-white">Nosso Compromisso com Você</h2>
          <p>
            O Que Promo é gratuito para os usuários. Somos mantidos através de parcerias de publicidade programática (Google AdSense) e 
            comissões oficiais de afiliação de lojas idôneas, sem nenhum custo extra no seu carrinho de compras.
          </p>
        </section>
      </div>
    </div>
  );
}
