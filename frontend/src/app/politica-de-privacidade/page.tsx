import type { Metadata } from "next";
import Link from "next/link";
import { Shield, Lock, Eye, FileText, ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Política de Privacidade | Que Promo",
  description: "Política de privacidade, conformidade com a LGPD e termos de monetização/cookies do Que Promo (quepromo.com.br).",
};

export default function PoliticaPrivacidadePage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6 text-gray-300">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Voltar para as ofertas
      </Link>

      <div className="border-b border-white/[0.08] pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3">
          <Shield className="w-3.5 h-3.5" />
          <span>LGPD & Conformidade Google AdSense</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Política de Privacidade</h1>
        <p className="text-sm text-gray-400 mt-2">
          Última atualização: Outubro de 2026 • Que Promo (quepromo.com.br)
        </p>
      </div>

      <div className="space-y-6 text-sm leading-relaxed">
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Eye className="w-4 h-4 text-rose-500" /> 1. Informações Gerais
          </h2>
          <p>
            O <strong>Que Promo</strong> (acessível através do domínio <strong>quepromo.com.br</strong>) é uma plataforma online 
            independente de agregação, auditoria histórica e comparação de preços de produtos comercializados no varejo brasileiro.
            Esta Política de Privacidade descreve como coletamos, usamos, armazenamos e protegemos os seus dados durante a navegação.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Lock className="w-4 h-4 text-emerald-400" /> 2. Coleta de Dados e Finalidade
          </h2>
          <p>
            O Que Promo preza pela mínima coleta de dados. Não exigimos cadastro obrigatório para busca, consulta de preços históricos 
            ou visualização de ofertas. Coletamos apenas:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-gray-400">
            <li><strong>Dados de Navegação Anônimos:</strong> Endereço IP aproximado, tipo de navegador, páginas visualizadas e tempo de permanência para fins estatísticos e prevenção de fraudes.</li>
            <li><strong>Alertas de Preço:</strong> Quando você cadastra voluntariamente um alerta de queda de valor, armazenamos seu e-mail ou identificador exclusivamente para o disparo da notificação.</li>
            <li><strong>Favoritos Locais:</strong> Itens salvos nos favoritos utilizam armazenamento local no seu navegador (LocalStorage) ou hashes anônimos, sem identificação pessoal direta.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-amber-400" /> 3. Google AdSense e Cookies de Terceiros
          </h2>
          <p>
            Utilizamos o <strong>Google AdSense</strong> para veiculação de anúncios quando você visita nosso site. 
            O Google, como fornecedor terceiro, utiliza cookies (incluindo o cookie DoubleClick DART) para exibir anúncios 
            baseados nas suas visitas anteriores ao nosso site ou a outros sites na internet.
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-gray-400">
            <li>Os usuários podem desativar o uso de publicidade personalizada acessando as <a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer" className="text-rose-400 hover:underline">Configurações de Anúncios do Google</a>.</li>
            <li>Como alternativa, você pode desativar o uso de cookies de fornecedores terceiros para publicidade personalizada acessando o portal <a href="https://www.aboutads.info" target="_blank" rel="noopener noreferrer" className="text-rose-400 hover:underline">www.aboutads.info</a>.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Shield className="w-4 h-4 text-blue-400" /> 4. Divulgação de Links de Afiliados
          </h2>
          <p>
            Em total transparência com nossos leitores e em conformidade com as diretrizes do FTC e PROCON: 
            o Que Promo participa de programas de afiliados oficiais, incluindo:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-gray-400">
            <li><strong>Programa de Associados da Amazon Brasil:</strong> Como associados da Amazon, podemos ser remunerados por compras qualificadas efetuadas através dos nossos links, sem qualquer acréscimo de custo para o consumidor.</li>
            <li><strong>Programa de Afiliados Mercado Livre:</strong> Links de produtos do Mercado Livre podem gerar comissões de indicação sem custo adicional para o comprador.</li>
            <li><strong>Programa de Afiliados Shopee Brasil:</strong> Redirecionamentos para ofertas da Shopee podem gerar remuneração comissionada para manutenção dos servidores e robôs da plataforma.</li>
            <li><strong>Magazine Luiza (Parceiro Magalu) e outras redes:</strong> Links devidamente identificados com parâmetros de parceria.</li>
          </ul>
          <p className="text-xs text-gray-400 italic">
            * Importante: A remuneração por afiliação não altera o preço final do produto para você e não influencia a imparcialidade dos nossos gráficos de histórico real de preços.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Lock className="w-4 h-4 text-purple-400" /> 5. Direitos do Titular (LGPD - Lei 13.709/2018)
          </h2>
          <p>
            Você tem total direito de solicitar a confirmação da existência de tratamento, o acesso aos seus dados cadastrados em alertas, 
            a correção de dados incompletos ou a eliminação dos seus dados da nossa base a qualquer momento, mediante requisição simples.
          </p>
        </section>

        <section className="space-y-3 border-t border-white/[0.08] pt-6">
          <h2 className="text-lg font-bold text-white">6. Contato do Encarregado de Dados</h2>
          <p>
            Para exercer seus direitos de privacidade, tirar dúvidas ou enviar sugestões sobre esta política, entre em contato diretamente 
            pelo canal oficial:
          </p>
          <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs">
            <p className="font-semibold text-white">Que Promo - Suporte & Privacidade</p>
            <p className="text-gray-400 mt-1">E-mail: <a href="mailto:contato@quepromo.com.br" className="text-rose-400 hover:underline">contato@quepromo.com.br</a></p>
            <p className="text-gray-400">Domínio Oficial: https://quepromo.com.br</p>
          </div>
        </section>
      </div>
    </div>
  );
}
