# Backlog — Que Promo

Registrado em 27/10/2026, a partir de 5 pesquisas (concorrentes, dores do consumidor, inovação, crescimento, viabilidade técnica).
Regra que vale para todas: nada de preço, desconto ou compatibilidade afirmados sem dado que sustente.

**Confiança da pesquisa:** a de viabilidade leu o código (confiável). As demais usaram poucas buscas na web e muitas fontes fracas; a de inovação não buscou na web. Trate como hipótese e valide antes de investir.

## Passo 0 — resultado (medido em 27/10/2026, produção)
**Histórico de preço:** dos 9756 itens disponíveis, só 118 têm 2+ pontos, 2 têm 5+ e **nenhum tem 14+**. O worker grava um ponto só na entrada do item e quando o preço muda (`scraper_worker.py:196-201` e `:267`), então preço parado = 1 ponto para sempre. Para "há quanto tempo observamos" use `created_at`, não a contagem de pontos.
→ **Ideias 1 e 2 (percentil e falso desconto) não são viáveis hoje.** Dá para afirmar só fatos simples ("preço igual desde DD/MM") até acumular variação.

**Campos por fonte:**
- **ML:** catálogo traz marca (55/59 produtos), modelo (49/59) e até 90 atributos. **GTIN/EAN: 0/59.** → garagem de celular viável pelo atributo; comparador por GTIN **não** é viável.
- **Shopee:** o feed tem `discount_percentage`, `global_category1/2` e `global_item_attributes`, mas os atributos vêm como IDs numéricos, sem nome legível de marca/modelo/GTIN. → só por título.
- **Lomadee:** campos `categories`, `options[].brands`, `metadata`; o conteúdo de `metadata` **não foi lido** (erro no script). Pendente.

**Termos dos programas (sobre redirecionar e injetar tag no clique):**
- **Shopee:** a página oficial lista 4 condutas proibidas (palavra-chave paga, site impróprio, fraude de cliques, e-mail sem consentimento). Não trata de redirecionamento, encurtador, extensão nem cupom. Os Termos completos não foram lidos.
- **ML:** página oficial bloqueou a leitura (403). Não confirmado.
- **Amazon BR:** o contrato exige usar os formatos de link rastreado fornecidos por eles (cláusula 1) e não deturpar a relação (cláusula 5). As Políticas do Programa, onde ficam as regras detalhadas, **não foram lidas**.
→ A suspeita de cloaking em `/r/` **segue não confirmada nem descartada**. Ler os Termos completos de cada programa antes de escalar tráfego.

## Faixa 1 — baratas, no seu diferencial (honestidade de preço)
1. **Preço justo estatístico:** "este preço está no percentil X dos últimos N dias", com selo de confiança e só para itens com histórico suficiente. Nunca como "previsão". Esforço 2-4 dias.
2. **Detector de falso desconto:** comparar o desconto anunciado com o histórico observado. Começar com um relatório interno dos 200 maiores descontos (também serve de conteúdo). Linguagem factual ("o preço era X há D dias").
3. **Sinais de confiança no card:** preço principal sempre sem cupom; aviso "o preço final pode variar no checkout"; preço à vista/Pix ao lado do parcelado; deixar claro que só levamos a lojas oficiais.
4. **Preço por unidade e aviso de kit:** extrair a quantidade do título (regex primeiro, LLM só nos casos ambíguos).
5. **Verificar um link:** página que recebe um link do Mercado Livre (API oficial) e mostra o histórico. Entrada de tráfego e fonte de dados.

## Faixa 2 — média
6. **Minha garagem, celular:** modelo → capa, película, carregador. Extrair o modelo do título por regex (e do atributo `MODEL` do catálogo ML, se existir). 3-5 dias. Risco: "iPhone 15" x "15 Pro".
7. **Comparador por GTIN, só no ML:** ler o GTIN em `/products/{id}`, coluna nova `gtin` (sem migrações: exige ALTER manual no `.db`). 1 dia para capturar, depois ampliar às outras lojas só se o dump do Passo 0 mostrar GTIN nelas. Sem GTIN, não mostra "mesmo produto".
8. **Canal WhatsApp/Telegram** com curadoria e histórico de preço nos posts.
9. **SEO programático com dado único** (série de preço, mínimo histórico). Páginas finas em massa são punidas pelo Google e ameaçam o AdSense.

## Faixa 3 — depois
- **Minha garagem, carro:** só os 15-20 modelos mais vendidos e itens de encaixe fácil. O endpoint de compatibilidade do ML teria saído do ar em 15/07/2026 (segundo resumos de busca; os docs deram 403, **não confirmado**). Risco alto de compatibilidade errada.
- **Lista de compras com menor total:** depende do comparador e do frete real (`free_shipping` é binário; Shopee/Lomadee fixam 0).
- **Dados abertos / API pública de histórico**, afiliação CPA em finanças e viagens, newsletter patrocinada: só com audiência e meses de histórico limpo.
- **Busca por foto:** ganho menor; testar CLIP em 500 produtos antes.

## Riscos a tratar antes de escalar
1. Termos dos programas de afiliado (redirecionamento, cupom, extensão).
2. AdSense/Google contra conteúdo fino de afiliado.
3. LGPD se coletar e-mail ou WhatsApp (opt-in explícito, descadastro fácil, segundo consentimento para newsletter).

## Pendências técnicas
- Mostrar na home só promoções com desconto verificado (hoje o contador inclui itens do ML sem preço de lista).
- Gerar mais feeds no painel da Shopee (o feed único tem 10 mil linhas, ~5058 passam no filtro).
- Ampliar o ML com `/products/search` além dos destaques (a busca de anúncios segue em 403).
- Tornar 30 dias o padrão do Lomadee no código (hoje só no `.env` da VPS).
- Confirmar como o frontend é publicado (não aparece no Vercel conectado a esta conta).
