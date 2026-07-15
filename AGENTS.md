# FranchStudy — 法语学习系统

## Stack

- **Backend**: Flask 2 + PostgreSQL (psycopg2), WSGI via gunicorn
- **Frontend**: Vue 3 (Composition API, `<script setup>`) + Vite 7 + Tailwind CSS 3 + Pinia + Vue Router 4
- **No TypeScript, no tests, no CI, no linter/formatter/pre-commit**

## Dev commands

```sh
# Backend (in backend/)
pip install -r requirements.txt
python app.py                    # Flask dev server on :5000
flask run                        # same
gunicorn app:app                 # production (installed in Dockerfile, not requirements.txt)

# Frontend (in frontend/)
npm install
npm run dev                      # Vite dev on :3000
npm run build                    # production build → dist/
```

## Architecture

- **Two-tier**: Flask REST API (`/api/auth/*`, `/api/spellingbee/*`) + Vue SPA
- **Hybrid data**: Some features use static JSON from `frontend/src/data/` (imported at build time), others hit the API + PostgreSQL
- **Auth**: JWT (HS256, 7-day expiry) in `localStorage`; `@token_required` decorator queries DB on every request
- **Base URL**: `/france/` in production (`VITE_BASE_URL`), dev proxies to `http://127.0.0.1:5000/api`

## Database

PostgreSQL database `franchdb` with 4 tables: `users`, `words`, `exercise_words`, `mistake_notebook`.

Data import:
```sh
# 1. Place JSON word data in backend/database/data/
# 2. Import into DB
python import_word.py
# 3. Split compound entries (e.g. "enchanté, e") into variant rows
python chaifen.py
```

DB config read from env vars: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` (defaults: `127.0.0.1:5432/franchdb/franchuser/franchpass`).

## Conjugation Practice page (`/conjugation`)

A view at `frontend/src/views/ConjugationPractice.vue` that:
- Loads conjugation data from static JSON files in `frontend/src/data/practice-sheets/`
- Lets users select verbs and download printable HTML (默写版/答案版)
- To add a new practice sheet, place a JSON file in `src/data/practice-sheets/` and import + register it in the `availableFiles` array inside the component
- JSON format: `{ id, name, title, tenses[], subjects[], verbs[{ name, meaning, practice[][], answer[][] }] }`

## Gotchas

- **No test files exist** despite `pytest` and `TestingConfig` being present in deps
- **SQL injection risk** in `backend/routes/auth_routes.py` — uses `%s` string interpolation (`%` operator) instead of parameterized queries
- **CORS wide open**: `origins: "*"` on all `/api/*` routes
- **gunicorn** is installed inside Dockerfiles only, not in `requirements.txt`
- **`utils/utils.py`** contains e-commerce cruft (`OrderStatus`, `PaymentMethod`) — unused, don't rely on it
- The two Dockerfiles (`Dockerfile.dev`, `Dockerfile.prod`) are currently identical
- Audio playback uses `useSegmentAudio` composable for segment-cued sentence dictation
