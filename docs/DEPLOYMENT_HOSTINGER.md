# Deploying TrendForge AI to Hostinger Shared Hosting

TrendForge runs on Hostinger's **Setup Python App** (Phusion Passenger). No
Docker, VPS, or desktop dependencies are required. The FastAPI (ASGI) backend is
served through a WSGI bridge, and the built React frontend is served by the same
app.

---

## 1. Directory structure on Hostinger

Place the project under your home directory, for example:

```
/home/uXXXXXXXX/
├── trendforge/                 # application root (Python app "Application root")
│   ├── backend/
│   │   ├── app/                # FastAPI application
│   │   ├── passenger_wsgi.py   # Passenger entry (exposes `application`)
│   │   ├── manage.py           # DB migrate / seed / backup CLI
│   │   ├── requirements.txt
│   │   └── .env                # your secrets (copied from .env.example)
│   └── frontend/
│       └── dist/               # built React app (index.html + assets/)
└── trendforge-data/            # writable workspace (DB is MySQL; logs/cache/exports here)
```

Build the frontend locally (`cd frontend && npm ci && npm run build`) and upload
`frontend/dist/`. You do **not** need Node.js on Hostinger.

---

## 2. Create the Python application

In hPanel → **Advanced → Python App → Create application**:

- **Python version:** 3.12 (or the latest available 3.x)
- **Application root:** `trendforge/backend`
- **Application URL:** your domain or subdomain
- **Application startup file:** `passenger_wsgi.py`
- **Application entry point:** `application`

Enter the app's virtualenv (hPanel shows the exact `source .../activate`
command) and install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Environment variables

Copy `backend/.env.example` to `backend/.env` and fill it in (or set the same
keys in the Python App's "Environment variables" panel). Minimum for production:

```
APP_ENV=production
SECRET_KEY=<random 48+ char string>
DATABASE_URL=mysql+pymysql://uXXXX_user:PASSWORD@localhost:3306/uXXXX_trendforge?charset=utf8mb4
GEMINI_API_KEY=<your Gemini key>
ALLOWED_ORIGINS=https://yourdomain.com
DATA_DIR=/home/uXXXXXXXX/trendforge-data
FRONTEND_DIST=/home/uXXXXXXXX/trendforge/frontend/dist
LOG_LEVEL=INFO
```

Never commit `.env` or expose `GEMINI_API_KEY`/`SECRET_KEY`. On shared hosting
the Gemini key is read from the environment (there is no OS credential store).

---

## 4. Database (MySQL)

Create a MySQL database and user in hPanel → **Databases → MySQL Databases**,
then put the credentials into `DATABASE_URL` as shown above. Development uses
SQLite automatically (leave `DATABASE_URL` blank); production uses MySQL — the
only change needed is the connection string.

Initialize the schema and seed defaults (run from the app's virtualenv, in
`backend/`):

```bash
python manage.py check      # verify connectivity + show resolved config
python manage.py initdb     # create tables + seed default sources/settings
```

Tables are created automatically and migrations are additive and non-destructive,
so re-running `initdb`/`migrate` never loses data.

---

## 5. Frontend build & deployment

On your machine:

```bash
cd frontend
cp .env.production.example .env.production   # usually leave VITE_API_BASE_URL blank
npm ci
npm run build
```

Upload the resulting `frontend/dist/` to `trendforge/frontend/dist/` and make
sure `FRONTEND_DIST` points at it. The backend serves `index.html`, hashed
assets under `/assets`, and falls back to `index.html` for client-side routes so
browser refresh on nested URLs (e.g. `/studio`) works. Because the UI is served
from the same origin as the API, no CORS configuration is needed.

If you deploy the UI under a subpath (e.g. `https://domain.com/app/`), build with
`VITE_BASE=/app/ npm run build`.

---

## 6. Running migrations & updating the app

To deploy an update:

```bash
# upload new code + new frontend/dist, then in backend/ (venv active):
pip install -r requirements.txt
python manage.py migrate
```

Finally click **Restart** on the Python App in hPanel so Passenger reloads the
new code.

---

## 7. Backups

```bash
python manage.py backup /home/uXXXXXXXX/trendforge-data/backups   # write a zip
python manage.py restore path/to/backup.zip                       # restore
```

The built-in `manage.py backup/restore` covers a SQLite workspace. For MySQL,
use Hostinger's database export/import (phpMyAdmin) or `mysqldump` for full
database backups; the app-level Export Center still exports individual projects.

---

## 8. Verifying the deployment

- `https://yourdomain.com/api/health` → `{"status":"ok","database":"connected"}`
- `https://yourdomain.com/docs` → Swagger UI
- `https://yourdomain.com/` → the app loads; refreshing `/studio` still works
- **Settings → AI Provider** → **Test connection** confirms Gemini works

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| 500 on every request / "Passenger error" | Check the app's stderr log in hPanel and `trendforge-data/logs/errors.log`. Usually a missing dependency or bad `DATABASE_URL`. |
| `ModuleNotFoundError` | Ensure `pip install -r requirements.txt` ran inside the app's virtualenv, then Restart. |
| DB connection errors | Re-check `DATABASE_URL` (user/password/db name), that the MySQL user has privileges, and run `python manage.py check`. |
| `caching_sha2_password` auth error | `cryptography` must be installed (it is in requirements.txt); re-run pip install. |
| UI loads but API calls fail | Confirm the UI is same-origin, or set `ALLOWED_ORIGINS` to the UI origin. |
| Assets 404 / blank page | Verify `FRONTEND_DIST` points at the uploaded `dist/`, and rebuild with the correct `VITE_BASE` if under a subpath. |
| Permission denied writing logs/cache | Point `DATA_DIR` (and optionally `LOG_DIRECTORY`, `CACHE_DIRECTORY`, `EXPORT_DIRECTORY`) at a writable folder in your home directory. |
| Background jobs seem idle | Passenger may idle-stop the process; jobs resume on the next request. Direct AI actions (analysis, content) run per-request and are unaffected. |

Changes are picked up after **Restart** in the Python App panel.
