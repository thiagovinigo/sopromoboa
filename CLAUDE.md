# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"QuePromo" — Brazilian deals aggregator / price-drop radar with affiliate link management. Python FastAPI backend + scraper worker (SQLite), Next.js 15 / React 19 / Tailwind frontend. Code comments, UI strings and README are in Portuguese (pt-BR); match that.

## Dois projetos (leia `MAPA-DOS-PROJETOS.md` antes de SEO, deploy ou Search Console)

Este repositório é **só o QuePromo** (`quepromo.com.br`). O **MercaGym** (`mercagym.com.br`) é outro projeto, em `C:\Users\User\buscafitness` (repo `thiagovinigo/mercagym`), com código, deploy e SEO próprios. Corrigir algo aqui não corrige o MercaGym. Frontend do QuePromo roda na **Vercel** (projeto `sopromoboa`; `git push` não publica); backend na VPS `/opt/sopromoboa`. O MercaGym inteiro roda na mesma VPS, em `/opt/mercagym`, com deploy pontual (nunca `deploy-mercagym.ps1`).

## Commands

Backend (run from `backend/`; a Windows venv lives at `backend/venv`, not committed):
```bash
.\venv\Scripts\activate
pytest -v                          # all tests (pytest.ini: pythonpath=., testpaths=tests)
pytest tests/test_pricing.py::test_name -v   # single test
python scraper_worker.py           # one scrape pass; add --loop for continuous (as in docker-compose)
uvicorn main:app --reload --port 8001
```
Swagger at `http://localhost:8001/docs`.

Frontend (from `frontend/`): `npm run dev` (port 3000), `npm run build`, `npm run lint`. No frontend tests exist.

Full stack: `pm2 start ecosystem.config.cjs` from the root (Next dev :3000, API :8001 via `backend/start.cjs`, worker via `backend/start_worker.cjs`; both spawn `backend/venv/Scripts/python.exe`). `docker-compose.yml` is an alternative but uses port **8000** for the API, while code defaults and PM2 use **8001**.

Deploy do backend (único script de deploy; **não publica o frontend**, que vai pela Vercel — ver `MAPA-DOS-PROJETOS.md`): `scripts/deploy-backend.ps1` runs pytest, tars `backend/`, scp's to the VPS and restarts the `api`/`worker` containers using `backend/docker-compose.vps.yml` + `.env.vps`.

## Architecture

**Backend (`backend/`, flat modules, no package)**
- `main.py` (~1900 lines) holds all FastAPI routes, Pydantic schemas, admin auth and background threads. Routes: `/api/deals*`, `/api/radar`, `/api/alerts`, `/api/favorites`, `/api/affiliates*`, `/api/admin/*`, `/api/worker/*`, `/api/agent/hunter/*`, and `/r/{product_id}` (click-tracking redirect that injects the affiliate tag at request time).
- `database.py`: SQLAlchemy engine; `DATABASE_URL` env var, defaulting to `backend/sopromoboa.db` with WAL enabled. `Base.metadata.create_all` runs on import in both `main.py` and `scraper_worker.py` — there are no migrations; schema changes need manual handling of the existing `.db`.
- Scraping pipeline: `scraper_worker.py` auto-discovers any function named `scrape_*` in `backend/scrapers/*.py` (add a store by adding such a function — no registration), runs them in a `ThreadPoolExecutor`, then per store: `normalize.normalize_listing` → `affiliate.build_affiliate_url` (using active rows in `affiliate_programs`) → `pricing.apply_price_change` (ignores <2% noise, 7-day drop window, tracks historic low) → writes `PriceHistoryModel` and triggers user alerts. `pricing.py` and `normalize.py` are pure and are what the tests cover (`tests/test_pricing.py`, `tests/test_affiliate.py`).
- Two background loops start from `main.py`'s startup hook: an hourly `lightning_robot.run_lightning_robot_cycle()` (gated by `feature_flags.LIGHTNING_ENABLED`, env `LIGHTNING_ENABLED=1`, off by default; promotes big discounts to "lightning" deals, prunes expired ones, re-enforces affiliate tags) and on-demand worker runs via `/api/worker/run`. `worker_state` is in-process memory. `store_hunter_agent.py` discovers/audits new stores; `telegram_notifier.py` posts deals (env `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`).
- Top-level `seed_*.py`, `fix_catalog_urls.py`, `check_deal.py` and `scripts/` are one-off catalog maintenance tools; `scratch/` is untracked ad-hoc audit scripts.

**Frontend (`frontend/src`)**: Next.js App Router. Pages under `app/` (`radar`, `produto/[id]`, `afiliados`, `alertas`, `ofertas-relampago`, `favoritos`, `admin`, …) call the API via `lib/api.ts` types/helpers; each module re-declares `API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"`. Alerts and favorites are anonymous: a random token in `localStorage` (`lib/alerts.ts`, `lib/favorites.ts`) is sent to the backend, which stores its SHA-256 hash. Product cards link to backend `/r/{id}` rather than store URLs directly.

## Gotchas

- Affiliate integrity is a core concern recent commits focus on: product URLs must be direct product pages (no search URLs, no Unsplash/placeholder images), Shopee short links get unshortened, and the owner's affiliate tags (Amazon, Mercado Livre, Shopee) are force-applied by `lightning_robot.py`. Keep that invariant when touching scrapers, `affiliate.py` or seed scripts.
- Admin auth lives in `admin_auth.py` and fails closed: with no `ADMIN_PASSWORD` env var the admin is disabled (no default password). CORS reads `ALLOWED_ORIGINS` (comma-separated, defaults to `*`). `lightning_robot.py` still hardcodes the affiliate tags; prefer env vars if you touch it.
- `*.db`, `.env`, `*.env`, `venv/`, `.next/` are gitignored; `sopromoboa.db` in the repo root is a local artifact, not the DB the backend uses by default (`backend/sopromoboa.db`).
