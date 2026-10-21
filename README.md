# Só Promo Boa 🔥
> **O Radar Oficial de Quedas de Preço & Agregador de Ofertas Reais do Brasil**

O **Só Promo Boa** é uma plataforma completa inspirada na arquitetura distribuída do `BuscaArmas` (FastAPI + Workers Concorrentes + Scrapers Modulares + Next.js), adaptada para monitorar **promoções legítimas, quedas reais de preço e gestão profissional de links de afiliados** no varejo brasileiro (Amazon Brasil, Mercado Livre, Magazine Luiza, KaBuM!, Shopee, etc.).

---

## 🏗️ Arquitetura do Sistema

```
sopromoboa/
├── backend/
│   ├── scrapers/              # Plugins de raspagem auto-descobertos dinamicamente
│   │   ├── amazon_deals.py    # Scraper de ofertas da Amazon Brasil
│   │   ├── mercadolivre_deals.py # Scraper de promoções do Mercado Livre
│   │   ├── feed_deals.py      # Agregador de feeds RSS / canais abertos
│   │   ├── sample_deals.py    # Seed curado com 12+ ofertas reais multidepartamento
│   │   └── price_utils.py     # Parser de moeda brasileira (R$) e descontos
│   ├── tests/                 # Suite de testes unitários (pytest)
│   │   ├── test_pricing.py    # Testes de regras de queda e janela de 7 dias
│   │   └── test_affiliate.py  # Testes de parsing e injeção de tags de afiliado
│   ├── database.py            # SQLite em modo WAL (concorrência total leitura/escrita)
│   ├── models.py              # Modelos SQLAlchemy (Products, PriceHistory, Stores, Alerts, Clicks, Affiliates)
│   ├── pricing.py             # Motor puro de detecção de quedas reais vs ruído (<2%)
│   ├── normalize.py           # Normalização de títulos, marcas e categorias
│   ├── affiliate.py           # Injeção de tags de comissão e conversor universal
│   ├── scraper_worker.py      # Worker multithread (ThreadPoolExecutor) com auto-discovery
│   ├── main.py                # API REST em FastAPI com CORS e paginação
│   └── start.cjs              # Helper para inicialização via PM2 / Node
│
├── frontend/                  # Aplicação Web Moderna (Next.js 15 + React 19 + Tailwind CSS)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx       # Vitrine principal com busca instantânea e filtros
│   │   │   ├── radar/         # Radar dedicado de Quedas de Preço recentes
│   │   │   ├── produto/[id]/  # Detalhes da oferta com gráfico histórico SVG e link de afiliado
│   │   │   ├── afiliados/     # Central de Gestão & Gerador de Links Comissionados
│   │   │   └── alertas/       # Central de Alertas privados (sem login/sem expor dados)
│   │   ├── components/        # Header, DealCard, PriceChart, AlertModal
│   │   └── lib/               # Clientes de API e gestão de tokens em localStorage
│
├── docker-compose.yml         # Orquestração em containers (API + Worker Loop + Frontend)
├── ecosystem.config.cjs       # Gerenciamento de processos PM2
└── README.md
```

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- **Python 3.10+** (testado e homologado no Python 3.12)
- **Node.js 18+** (testado no Node.js v26 / v22)

---

### 2. Inicializando o Backend & Worker

No diretório `backend`:
```bash
cd backend

# Ativar o ambiente virtual (já configurado no projeto)
.\venv\Scripts\activate

# Executar a suíte de testes unitários
pytest -v

# Executar o scraper worker para varrer e sincronizar ofertas
python scraper_worker.py

# Iniciar a API FastAPI (porta 8001)
uvicorn main:app --reload --port 8001
```
> Documentação Swagger interativa disponível em: `http://localhost:8001/docs`

---

### 3. Inicializando o Frontend

No diretório `frontend`:
```bash
cd frontend

# Executar o servidor de desenvolvimento (porta 3000)
npm run dev
```
> Acesse no navegador: `http://localhost:3000`

---

### 4. Executando com PM2 (Ambiente Completo)

Na raiz do projeto:
```bash
pm2 start ecosystem.config.cjs
pm2 status
pm2 logs
```

---

## 💡 Recursos Principais

### 1. Detecção Rigorosa de Quedas de Preço (`pricing.py`)
- **Filtro Anti-Ruído:** Oscilações de centavos (<2%) são ignoradas para não poluir o radar com falsas promoções.
- **Janela Ativa de 7 Dias:** Apenas itens que reduziram de preço dentro da janela de 7 dias recebem o selo de queda ativa.
- **Menor Preço Histórico:** Registra o menor valor que o produto já atingiu na plataforma para indicar quando é o melhor momento de compra.

### 2. Motor de Scraping Modular (`scrapers/`)
- **Plugin System Dinâmico:** Para adicionar uma nova loja ou agregador, basta criar um arquivo `.py` na pasta `backend/scrapers/` contendo uma função iniciada por `scrape_nome_loja()`. O worker descobre e executa automaticamente sem alterar o código principal.
- **Execução Paralela:** Roda através de `ThreadPoolExecutor` com isolamento de transações de banco de dados por loja.

### 3. Sistema de Gestão & Geração de Links de Afiliados (`/afiliados`)
- **Gerador Universal:** Permite colar qualquer link de produto de grandes marketplaces (Amazon, Magalu, Mercado Livre, KaBuM!, Shopee) e gerar a URL comissionada com tags e UTMs (`utm_source=sopromoboa`, `utm_medium=redes_sociais`).
- **Redirecionamento Seguro (`/r/{id}`):** Os cards do site apontam para rotas de redirecionamento interno que auditam o clique e injetam a tag de afiliado correta em tempo de execução.
- **Configuração de Tags:** Cadastre ou edite suas tags de comissão diretamente na tabela `affiliate_programs`.

### 4. Alertas Privados e Seguros (`/alertas`)
- **Zero Fricção:** Os usuários podem criar alertas para preços ou descontos específicos sem necessidade de cadastro, senhas ou informar telefone/e-mail.
- **Token Anônimo:** A identidade é gerenciada por um token criptográfico de 256 bits armazenado exclusivamente no `localStorage` do navegador do usuário e comparado via hash SHA-256 no backend.
