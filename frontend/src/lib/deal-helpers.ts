import { Deal } from "./api";

export interface DealThermometer {
  status: "opportunity" | "regular" | "warning";
  label: string;
  badgeClass: string;
  icon: string;
  tag: string;
  explanation: string;
}

/**
 * Motor de Auditoria do Termômetro:
 * Analisa o histórico e variações do produto para alertar se é oportunidade real
 * ou se é uma "metade do dobro" / preço inflado com desconto maquiado.
 */
export function getDealThermometer(deal: Deal): DealThermometer {
  // Preço aumentou recentemente ou base inflada com falso desconto
  const isRecentIncrease = Boolean(deal.previous_price && deal.price > deal.previous_price);
  const isInflatedDiscount = Boolean(
    deal.lowest_historic_price &&
    deal.price > deal.lowest_historic_price * 1.35 &&
    deal.discount_percent < 8
  );

  if (isRecentIncrease || isInflatedDiscount) {
    return {
      status: "warning",
      label: "Alerta: Preço Inflado",
      tag: "CILADA",
      badgeClass: "bg-red-500/15 text-red-400 border-red-500/30",
      icon: "⚠️",
      explanation: "Atenção: este item sofreu aumento recente ou tem desconto maquiado. Recomendamos aguardar nova queda.",
    };
  }

  // Menor preço histórico comprovado ou super desconto acima de 25%
  if (
    deal.is_all_time_low ||
    deal.discount_percent >= 25 ||
    (deal.price_dropped === 1 && deal.discount_percent >= 15)
  ) {
    return {
      status: "opportunity",
      label: "Oportunidade Real",
      tag: "MENOR PREÇO",
      badgeClass: "bg-emerald-500/15 text-emerald-300 border-emerald-500/35",
      icon: "🟢",
      explanation: "Auditado pelo Que Promo: este produto atingiu o menor valor registrado recentemente.",
    };
  }

  // Preço padrão de mercado
  return {
    status: "regular",
    label: "Preço Padrão",
    tag: "REGULAR",
    badgeClass: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    icon: "🟡",
    explanation: "Preço médio de mercado. Bom valor, mas sem uma queda drástica nos últimos dias.",
  };
}

/**
 * Gera o pitch persuasivo de 1 frase para o compartilhamento de WhatsApp.
 */
function getCategoryPitch(title: string, category: string): string {
  const t = title.toLowerCase();

  if (t.includes("fone") || t.includes("headset") || t.includes("bluetooth") || t.includes("airpod")) {
    return "Som limpo com graves fortes e bateria para o dia todo. 🎧";
  }
  if (t.includes("cortador") || t.includes("barbeador") || t.includes("shaver")) {
    return "Corte rente e sem irritação para manter o visual alinhado em casa. ✂️";
  }
  if (t.includes("air fryer") || t.includes("fritadeira") || t.includes("panela")) {
    return "Praticidade na cozinha para receitas crocantes sem óleo e sem sujeira. 🍳";
  }
  if (t.includes("smartwatch") || t.includes("relogio") || t.includes("pulseira")) {
    return "Monitore treinos, saúde e notificações direto no seu pulso. ⌚";
  }
  if (t.includes("creatina") || t.includes("whey") || t.includes("suplemento")) {
    return "Pureza e absorção rápida para acelerar seus resultados nos treinos. 💪";
  }
  if (t.includes("wd-40") || t.includes("ferramenta") || t.includes("furadeira")) {
    return "Essencial para manutenção rápida, soltar peças e proteger contra ferrugem. 🛠️";
  }
  if (t.includes("ssd") || t.includes("gamer") || t.includes("monitor") || t.includes("rtx")) {
    return "Desempenho máximo para zerar travamentos e acelerar seus jogos e trabalho. ⚡";
  }
  return "Qualidade comprovada com excelente custo-benefício para aproveitar enquanto durar. ✨";
}

/**
 * Formata o link oficial de compartilhamento no WhatsApp com a copy campeã de conversão.
 */
export function getWhatsAppShareUrl(deal: Deal): string {
  const formatBRL = (val: number) =>
    val.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const pitch = getCategoryPitch(deal.title, deal.category);
  const refOld = deal.previous_price || deal.list_price;
  const oldPriceLine = refOld && refOld > deal.price ? `De: ~${formatBRL(refOld)}~\n` : "";
  const discountLine = deal.discount_percent > 0 ? `🤑 Desconto de *${deal.discount_percent}% OFF*\n` : "";
  const couponLine = deal.coupon_code ? `🎟 Cupom: *${deal.coupon_code}*\n` : "";
  const shippingLine = deal.free_shipping === 1 ? `🚚 *Frete Grátis disponível*\n` : "";

  const text =
    `🔥 *OLHA ESSA OFERTA NO QUE PROMO!*\n\n` +
    `*${deal.title}*\n\n` +
    `_${pitch}_\n\n` +
    `${oldPriceLine}` +
    `💥 *Por: ${formatBRL(deal.price)}*\n` +
    `${discountLine}` +
    `${couponLine}` +
    `${shippingLine}\n` +
    `🛒 *COMPRE AQUI COM DESCONTO* 👇\n` +
    `https://quepromo.com.br/produto/${deal.id}\n\n` +
    `🌐 _Auditado em quepromo.com.br_`;

  return `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
}
