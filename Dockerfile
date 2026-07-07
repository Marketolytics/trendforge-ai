# TrendForge AI — single-image build for a persistent host (Render, Fly.io, VPS).
# Stage 1 builds the React frontend; stage 2 runs FastAPI (uvicorn), which also
# serves the built frontend and runs the background job worker.

# ---- Stage 1: build the frontend ----
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python runtime ----
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production

WORKDIR /app

# Install Python dependencies first (better layer caching).
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install -r backend/requirements.txt

# Backend source + built frontend.
COPY backend/ ./backend/
COPY --from=frontend /app/frontend/dist ./frontend/dist

# The backend co-hosts the built frontend from here.
ENV FRONTEND_DIST=/app/frontend/dist

WORKDIR /app/backend
EXPOSE 8000

# Bind to the platform-provided port (Render/Fly set $PORT); default 8000 locally.
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
