# Mapa dos projetos: QuePromo e MercaGym

Leia isto antes de mexer em SEO, deploy ou Search Console. **São dois projetos, dois repositórios, dois domínios e duas formas de publicar.** Uma mudança num repositório não afeta o outro site.

## Visão geral

| | QuePromo | MercaGym |
|---|---|---|
| Domínio | `quepromo.com.br` | `mercagym.com.br` |
| Foco | Tudo das lojas (geral, inclui tênis) | Só treino/fitness (suplementos, moda e acessórios fitness) |
| Pasta local | `C:\Users\User\sopromoboa` | `C:\Users\User\buscafitness` |
| Repositório | `thiagovinigo/sopromoboa` | `thiagovinigo/mercagym` (privado) |
| `clickref` Awin | `quepromo` | `mercagym` |
| Frontend roda em | **Vercel**, projeto `sopromoboa` | **VPS** (Docker, atrás do Traefik) |
| Backend roda em | **VPS**, `/opt/sopromoboa` | **VPS**, `/opt/mercagym` |
| Banco | `backend/sopromoboa.db` (volume na VPS) | `/data/mercagym.db` (volume na VPS) |

A VPS é a mesma para os dois (Locaweb, `191.252.191.189`, usuário `root`, chave `~/.ssh/buscarmas_vps`). Ela tem ~2 GB divididos com outros sites e o swap fica quase cheio. Cuidado com builds pesados lá.

O nome "sopromoboa" é o começo do QuePromo. A fase 1 do rename (marca, `utm_source`, pacote) está feita. Banco, pasta/volume/containers da VPS, repo do GitHub, chaves `sopromoboa_*_token` do navegador e IDs de afiliado seguem com o nome antigo de propósito: trocar sem migração perde comissão ou dados dos usuários.

## Como publicar

### QuePromo: backend (API + worker)
1. A partir da raiz: `.\scripts\deploy-backend.ps1`.
2. O script roda `pytest`, empacota `backend/` (sem `venv`, `.env` nem `*.db`), envia por `scp` e reinicia os containers `api` e `worker` na VPS com `backend/docker-compose.vps.yml` e `.env.vps`.
3. Não envia banco, então não sobrescreve produção.

### QuePromo: frontend (Next.js)
- Está ligado ao projeto Vercel `sopromoboa` (`frontend/.vercel/project.json`: `projectId prj_cUzFpXzaFkbeveVyHKiMfnbD3ETQ`, `orgId team_nlQFHL0mqQiI3wpTq8XyC3Fg`). A pasta `.vercel` é ignorada pelo git.
- **`git push` não publicou o frontend** (verificado em 12/11/2026: o commit `0ea8bb5` estava na `main` e o site seguia com o comportamento antigo). O caminho provável é pela CLI: `cd frontend; vercel --prod`.
- O conector da Vercel do Claude devolve 403 ao listar os deploys deste projeto e só enxerga o projeto `nutri`. Para acompanhar o deploy, use a CLI (`vercel --scope <time> list sopromoboa`) ou o painel.
- **A confirmar:** se existe integração Git na Vercel. Até confirmar, não assumir que o push publica.

### MercaGym (frontend, API e worker)
- Tudo roda em Docker na VPS (`mercagym-api`, `mercagym-worker-1`, `mercagym-frontend`) em `/opt/mercagym`.
- Deploy **pontual**: `tar` dos arquivos alterados por ssh e `docker compose build frontend` (ou os serviços afetados).
  - Frontend é imagem: precisa reconstruir. Use `DOCKER_BUILDKIT=0 docker build --memory=650m --memory-swap=900m` e pare só o worker do mercagym durante o build.
  - Variáveis do `.env` só recarregam com `docker compose up -d --force-recreate`.
- **Não usar `scripts/deploy-mercagym.ps1`.** O README do repositório diz que não é confiável, e a memória do projeto registra que ele já sobrescreveu o banco. Mesmo com a correção do commit `9cfd57f`, o procedimento acordado segue sendo o pontual.
- Segredos só em `backend/.env` na VPS (`chmod 600`). O código nunca leva valor padrão de segredo.
- Sem painel admin neste site, por decisão do dono.

## Search Console
Propriedades (prefixo de URL) na conta do dono:
- `https://quepromo.com.br/` e `https://mercagym.com.br/`.
- Existe também `buscaarmas.com.br` (propriedade de domínio). Não faz parte destes dois projetos. Não mexer sem perguntar.

URL direta do relatório de indexação: `https://search.google.com/search-console/index?resource_id=https%3A%2F%2F<dominio>%2F`.

Antes de "corrigir" algo no código por causa do Search Console, descubra **de qual site** é o problema e **em qual repositório** a correção deve entrar. Cada site tem robots, sitemap e metadados próprios.

## Estado do SEO (12/11/2026)
- Os dois `robots.txt` bloqueiam só `/r/`, `/api/` e (QuePromo) `/admin`. O `/r/` é o redirecionador de afiliado e o bloqueio é intencional. Não "corrigir".
- Maior parte dos não indexados é "Detectada, mas não indexada": 2.893 (MercaGym) e 5.692 (QuePromo). Não tem correção direta. Caminho: enxugar o sitemap e reforçar links internos.
- Sitemaps: MercaGym ~6.372 URLs, QuePromo ~28.479 URLs.
- Validações iniciadas em 12/11/2026: QuePromo 5xx (8) e 404 (102); MercaGym 404 (6) e soft 404 (11). Rever o relatório depois de alguns dias a duas semanas.
- QuePromo: `busca-personalizada` ganhou `noindex, follow` no commit `0ea8bb5`. **Pendente de publicar no frontend (Vercel).**
- MercaGym: já serve `noindex, follow` no `/?q=`. Essa correção vem do repositório dele, não do `sopromoboa`.

## Checklist antes de agir
1. Qual site? Qual repositório? (tabela acima)
2. Onde esse código roda? (Vercel, VPS/Docker)
3. Como publica e o que isso arrisca? (banco, memória da VPS, segredos)
4. Depois de publicar, confirmar **no ar**, não só no commit:
   ```bash
   curl -s "https://quepromo.com.br/busca-personalizada?q=whey" | grep -o '<meta name="robots"[^>]*>'
   curl -s "https://mercagym.com.br/busca-personalizada?q=whey" | grep -o '<meta name="robots"[^>]*>'
   ```
5. Só validar no Search Console depois que a correção estiver no ar.

## Invariantes (valem para os dois)
- URLs de produto são páginas diretas (sem busca, sem placeholder). Tags de afiliado do dono (Amazon, Mercado Livre, Shopee) são força-aplicadas. Ver `CLAUDE.md`.
- Admin do QuePromo falha fechado sem `ADMIN_PASSWORD`.
- Nunca commitar `.env`, `*.db`, chaves ou tokens.
