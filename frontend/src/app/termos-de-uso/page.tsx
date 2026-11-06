import type { Metadata } from "next";
import Link from "next/link";
import { FileCheck, AlertCircle, ShoppingBag, ArrowLeft, ShieldAlert, Scale } from "lucide-react";

export const metadata: Metadata = {
  title: "Termos de Uso & Avisos Legais | Que Promo",
  description: "Termos e condições de uso, isenção de responsabilidade sobre preços, qualidade e estoque da plataforma Que Promo (quepromo.com.br).",
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
          <span>Condições Gerais de Uso & Proteção Jurídica</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Termos de Uso & Avisos Legais</h1>
        <p className="text-sm text-gray-400 mt-2">
          Última atualização: Novembro de 2026 • Que Promo (quepromo.com.br)
        </p>
      </div>

      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200/90 text-xs space-y-2">
        <p className="font-bold flex items-center gap-2 text-sm text-amber-300">
          <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
          Resumo Jurídico e Isenção de Fornecimento
        </p>
        <p>
          O <strong>Que Promo</strong> é um agregador e comparador independente de preços e promoções. <strong>Não somos loja virtual, não vendemos mercadorias e não recebemos pagamentos.</strong> Toda transação, pagamento, envio, garantia legal e emissão de nota fiscal ocorrem exclusivamente no site do lojista parceiro onde a compra é concluída.
        </p>
      </div>

      <div className="space-y-6 text-sm leading-relaxed">
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShoppingBag className="w-4 h-4 text-rose-500" /> 1. Natureza do Serviço e Papel da Plataforma
          </h2>
          <p>
            O <strong>Que Promo</strong> opera como um serviço informativo e comparativo de preços. 
            O Que Promo <strong>não comercializa</strong> diretamente nenhum produto físico ou digital apresentado nas suas páginas. 
            Nossa tecnologia automatizada apenas pesquisa, consolida, audita o histórico e exibe preços praticados por lojas parceiras terceiras 
            (como Amazon, Mercado Livre, Shopee, Magazine Luiza, Netshoes, Centauro, entre outras).
          </p>
          <p>
            Nos termos do Art. 19 da Lei Federal nº 12.965/2014 (Marco Civil da Internet), o Que Promo não responde civilmente pelos conteúdos, ofertas e condutas comerciais dos lojistas parceiros indexados.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400" /> 2. Variação de Preços, Estoque e Erro Notório (Preço Vil)
          </h2>
          <p>
            Embora nossos robôs atualizem os dados continuamente em ciclos frequentes, as lojas virtuais terceiras possuem total autonomia 
            para alterar preços, encerrar cupons e esgotar estoques sem aviso prévio.
          </p>
          <ul className="list-disc pl-5 space-y-2 text-gray-400">
            <li>
              Em caso de divergência entre o preço anunciado no Que Promo e o preço no carrinho da loja parceira, <strong>prevalece invariavelmente o valor e condição exibidos no site final da loja vendedora</strong>.
            </li>
            <li>
              <strong>Erro Notório / Preço Vil:</strong> Erros crasso de precificação causados por falhas técnicas de lojistas (como produtos anunciados por fração ínfima do seu valor real de mercado) não vinculam o Que Promo nem configuram oferta exigível, em conformidade com o princípio da boa-fé objetiva e a vedação ao enriquecimento sem causa (Art. 884 do Código Civil e jurisprudência pacífica do STJ).
            </li>
            <li>
              O Que Promo não se responsabiliza por compras não concretizadas decorrentes de esgotamento de estoque ou cancelamento unilateral por parte dos lojistas.
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Scale className="w-4 h-4 text-emerald-400" /> 3. Responsabilidade sobre Qualidade, Vício do Produto, Entrega e Garantia
          </h2>
          <p>
            Em conformidade com os artigos 12, 13 e 18 do Código de Defesa do Consumidor (CDC):
          </p>
          <ul className="list-disc pl-5 space-y-2 text-gray-400">
            <li>
              Todo o processo de checkout, faturamento, pagamento, emissão de nota fiscal, envio, rastreamento e atendimento pós-venda 
              (incluindo trocas e devoluções garantidas pelo Código de Defesa do Consumidor) é de responsabilidade estrita da 
              <strong> loja parceira onde a compra foi efetivamente concluída e do fabricante da mercadoria</strong>.
            </li>
            <li>
              O Que Promo não realiza vistoria física dos produtos e não responde por defeitos de fabricação, atrasos de transportadoras ou divergências de especificações técnicas originadas nos cadastros das lojas de destino.
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-blue-400" /> 4. Transparência e Relação de Afiliados (Compliance Conar & FTC)
          </h2>
          <p>
            O Que Promo atua com total transparência com seus visitantes. Participamos de programas de afiliados comerciais (Amazon Associados, Mercado Livre, Shopee, Awin, Lomadee, etc.). 
            Ao clicar em determinados links e finalizar uma compra na loja parceira, nossa plataforma pode receber uma comissão financeira. 
            <strong>Essa remuneração não encarece o produto para você</strong> e é utilizada para manter os servidores e os robôs de detecção de promoções em funcionamento contínuo e gratuito.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">5. Propriedade Intelectual</h2>
          <p>
            As marcas, logotipos e fotos dos produtos pertencem aos seus respectivos fabricantes e varejistas licenciados. 
            A marca Que Promo, o código-fonte dos algoritmos de detecção de queda e o design da interface são protegidos 
            pela legislação de propriedade intelectual brasileira.
          </p>
        </section>

        <section className="space-y-3 border-t border-white/[0.08] pt-6">
          <h2 className="text-lg font-bold text-white">6. Canal de Atendimento</h2>
          <p>
            Dúvidas sobre o funcionamento do radar ou relatórios de erros nos anúncios podem ser enviados para:
          </p>
          <p className="text-rose-400 font-semibold">contato@quepromo.com.br</p>
        </section>
      </div>
    </div>
  );
}
