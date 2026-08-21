# ReconAI Changelog

## 4.1.0

### Deploy fixes
- CORS middleware (`CORS_ORIGINS` env, supports `*`)
- Postgres URL normalization for Supabase (`postgresql://` → `postgresql+psycopg://`)
- Frontend `API_BASE` via `localStorage.apiBase` or `window.RECONAI_API_BASE` (Vercel → Render/Koyeb)

### Features
- Owner Drawings endpoint `POST /api/drawings`
- Owner Drawings form on Expenses page

### Version
- Health endpoint reports `4.1.0`

Replace `app/main.py` and `static/index.html` from the Perfect ZIP if those files on GitHub are still older.
