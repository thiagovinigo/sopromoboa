import type { Metadata } from "next";
import Link from "next/link";
import { FileCheck, AlertCircle, ShoppingBag, ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Termos de Uso | Que Promo",
  description: "Termos e condições de uso da plataforma de monitoramento de promoções Que Promo (quepromo.com.br).",
};

export default function TermosDeUsoPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6 text-gray-300">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Voltar para as ofertas
      </Link>

      <div className="border-b border-white/[0.08] pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-3">
          <FileCheck className="w-3.5 h-3.5" />
          <span>Condições Gerais de Uso</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Termos de Uso</h1>
        <p className="text-sm text-gray-400 mt-2">
          Última atualização: Outubro de 2026 • Que Promo (quepromo.com.br)
        </p>
      </div>

      <div className="space-y-6 text-sm leading-relaxed">
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShoppingBag className="w-4 h-4 text-rose-500" /> 1. Natureza do Serviço
          </h2>
          <p>
            O <strong>Que Promo</strong> é um serviço agregador informativo e comparativo de preços. 
            O Que Promo <strong>não comercializa</strong> diretamente nenhum produto físico ou digital apresentado nas suas páginas. 
            Nossa tecnologia automatizada apenas pesquisa, consolida, audita o histórico e exibe preços praticados por lojas parceiras terceiras 
            (como Amazon, Mercado Livre, Shopee, Magazine Luiza, entre outras).
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400" /> 2. Variação de Preços e Disponibilidade de Estoque
          </h2>
          <p>
            Embora nossos robôs atualizem os dados continuamente (em ciclos horários), as lojas virtuais terceiras possuem total autonomia 
            para alterar preços, encerrar cupons e esgotar estoques sem aviso prévio.
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-gray-400">
            <li>Em caso de divergência entre o preço anunciado no Que Promo e o preço no carrinho da loja parceira, <strong>prevalece sempre o valor exibido no site final da loja vendedora</strong>.</li>
            <li>O Que Promo não se responsabiliza por compras não concretizadas decorrentes de esgotamento de estoque ou cancelamento por parte dos lojistas.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-emerald-400" /> 3. Transações e Entregas
          </h2>
          <p>
            Todo o processo de checkout, faturamento, pagamento, emissão de nota fiscal, envio, rastreamento e atendimento pós-venda 
            (incluindo trocas e devoluções garantidas pelo Código de Defesa do Consumidor) é de responsabilidade estrita da 
            <strong> loja parceira onde a compra foi efetivamente concluída</strong>.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">4. Propriedade Intelectual</h2>
          <p>
            As marcas, logotipos e fotos dos produtos pertencem aos seus respectivos fabricantes e varejistas licenciados. 
            A marca Que Promo, o código-fonte dos algoritmos de detecção de queda e o design da interface são protegidos 
            pela legislação de propriedade intelectual brasileira.
          </p>
        </section>

        <section className="space-y-3 border-t border-white/[0.08] pt-6">
          <h2 className="text-lg font-bold text-white">5. Canal de Atendimento</h2>
          <p>
            Dúvidas sobre o funcionamento do radar ou relatórios de erros nos anúncios podem ser enviados para:
          </p>
          <p className="text-rose-400 font-semibold">contato@quepromo.com.br</p>
        </section>
      </div>
    </div>
  );
}
