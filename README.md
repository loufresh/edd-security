
# EDD Security — Starter Kit (v0.5)

**UI React completa** (SPA), **Runs API**, **CORS** habilitado y **onboarding guiado**.

## Qué incluye la v0.5
- API:
  - `/runs/` para listar ejecuciones (tenant/project aware).
  - CORS para servir dashboard desde `localhost:8080`.
- Frontend (SPA con React via CDN):
  - Tabs: Onboarding, Jobs, Runs, Alertas (SSE + historial), Notificaciones, API Keys.
  - Crear job, ejecutar **Run Now**, ver salida detallada.
  - Ingreso (org signup/login), status de token/tenant.
  - Panel de notificaciones (dispara evento vía webhook ingest).
- Sigue soportando: multi-tenant, roles granulares por proyecto, webhooks de salida, WhatsApp/Email/Slack/Telegram, SSE.

## Levantar
```bash
cp .env.example .env
docker compose up --build
```
- Dashboard: http://localhost:8080
- API Docs: http://localhost:8000/docs

## Demo rápido
1) En el Dashboard → **Org Signup**.
2) En Onboarding → crea un job `automation.scrape_prices` y presiona **Run Now**.
3) En **Runs** → observa la ejecución y salida.
4) En **Alertas** → mira el feed en vivo (si triggeras `security.monitor_logs` con umbral bajo).
