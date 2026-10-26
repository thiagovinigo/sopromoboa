import type { Deal } from "./api";

// Descontos acima do teto costumam ser preço de lista inflado pela própria loja.
const MIN_FEATURED_DISCOUNT = 20;
const MAX_FEATURED_DISCOUNT = 60;
const RATING_BASELINE = 4;
const RATING_WEIGHT = 10;

const SWEET_SPOT_DISCOUNT = 50;

// Medicamentos não entram na vitrine: a divulgação de remédios ao público é restrita pela Anvisa e pelo AdSense.
const MEDICINE_PATTERN = /gen[eé]rico|comprimidos?|c[aá]psulas?|\bmcg\b|\b\d+\s?mg\b|medicamento|\bbula\b/i;
// Assinaturas e serviços não são produtos de vitrine.
const NON_PRODUCT_PATTERN = /\bmeli\s*\+|assinatura|vale[- ]presente/i;

/** Premia descontos até a faixa de 50% e penaliza os acima dela, que costumam ser preço de lista inflado. */
function score(deal: Deal): number {
  const discount = deal.discount_percent;
  const effectiveDiscount = discount <= SWEET_SPOT_DISCOUNT ? discount : SWEET_SPOT_DISCOUNT - (discount - SWEET_SPOT_DISCOUNT);
  const ratingBonus = deal.rating ? (deal.rating - RATING_BASELINE) * RATING_WEIGHT : 0;
  return effectiveDiscount + ratingBonus;
}

/** Dentro de uma loja, evita repetir a mesma categoria enquanto houver outras disponíveis. */
function spreadCategories(items: Deal[]): Deal[] {
  const remaining = [...items];
  const used = new Set<string>();
  const result: Deal[] = [];
  while (remaining.length > 0) {
    let index = remaining.findIndex((deal) => !used.has(deal.category));
    if (index === -1) {
      used.clear();
      index = 0;
    }
    const [next] = remaining.splice(index, 1);
    result.push(next);
    used.add(next.category);
  }
  return result;
}

/**
 * Escolhe ofertas variadas para a vitrine: filtra descontos suspeitos, ordena por desconto e nota
 * e intercala as lojas (uma oferta de cada antes de repetir), variando as categorias dentro de cada loja.
 */
export function pickFeatured(deals: Deal[], size: number): Deal[] {
  const seenTitles = new Set<string>();
  const eligible = deals
    .filter(
      (d) =>
        Boolean(d.image_url) &&
        !MEDICINE_PATTERN.test(d.title) &&
        !NON_PRODUCT_PATTERN.test(d.title) &&
        d.discount_percent >= MIN_FEATURED_DISCOUNT &&
        d.discount_percent <= MAX_FEATURED_DISCOUNT
    )
    .sort((a, b) => score(b) - score(a))
    .filter((d) => {
      const title = d.title.trim().toLowerCase();
      if (seenTitles.has(title)) return false;
      seenTitles.add(title);
      return true;
    });

  const bySource = new Map<string, Deal[]>();
  for (const deal of eligible) {
    bySource.set(deal.source, [...(bySource.get(deal.source) ?? []), deal]);
  }

  const queues = Array.from(bySource.values()).map(spreadCategories); // lojas já do melhor para o pior
  const picked: Deal[] = [];
  for (let depth = 0; picked.length < size; depth++) {
    const round = queues.filter((queue) => depth < queue.length).map((queue) => queue[depth]);
    if (round.length === 0) break;
    picked.push(...round.slice(0, size - picked.length));
  }
  return picked;
}
