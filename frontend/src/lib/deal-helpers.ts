import { Deal } from "./api";

export interface DealThermometer {
  status: "opportunity" | "declared" | "regular" | "warning";
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

  // Só o nosso histórico sustenta o selo de oportunidade: desconto declarado pela loja, sozinho, não basta.
  const hasConfirmedDrop = deal.price_dropped === 1 && deal.discount_percent >= 15;
  if (deal.is_all_time_low || hasConfirmedDrop) {
    return {
      status: "opportunity",
      label: deal.is_all_time_low ? "Menor preço registrado" : "Queda confirmada",
      tag: deal.is_all_time_low ? "MENOR PREÇO" : "QUEDA",
      badgeClass: "bg-emerald-500/15 text-emerald-300 border-emerald-500/35",
      icon: "🟢",
      explanation: deal.is_all_time_low
        ? "Este é o menor preço que o radar do Que Promo já registrou para este produto."
        : "O radar do Que Promo registrou uma queda de preço neste produto entre duas varreduras.",
    };
  }

  // Desconto informado pela própria loja, sem histórico nosso para confirmar
  if (deal.discount_percent >= 10) {
    return {
      status: "declared",
      label: "Desconto da loja",
      tag: "INFORMADO PELA LOJA",
      badgeClass: "bg-sky-500/15 text-sky-300 border-sky-500/30",
      icon: "🏷️",
      explanation: `A loja informa ${Math.round(deal.discount_percent)}% de desconto sobre o preço de lista. Ainda não temos histórico para confirmar.`,
    };
  }

  // Sem desconto declarado e sem histórico: só acompanhamento
  return {
    status: "regular",
    label: "Em acompanhamento",
    tag: "SEM HISTÓRICO",
    badgeClass: "bg-gray-500/15 text-gray-300 border-gray-500/30",
    icon: "⚪",
    explanation: "Estamos acompanhando este preço. O histórico aparece conforme ele variar nas próximas varreduras.",
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
