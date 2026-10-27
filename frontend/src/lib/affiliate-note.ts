/** Aviso de afiliado exibido junto às vitrines (a Amazon exige a frase de Associado). */
export function affiliateNote(store: string): string {
  const disclosure =
    store === "Amazon"
      ? "Como Associado da Amazon, o Que Promo ganha com compras qualificadas."
      : "O Que Promo pode receber comissão pelas compras feitas pelos links.";
  return `${disclosure} Preços informados pela loja ou pela comunidade; confirme o valor final no site da loja.`;
}
