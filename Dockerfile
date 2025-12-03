# =============================================================================
# Dockerfile — Sistema de Gestión de Crisis IPR
# Multi-stage build para imagen optimizada
# =============================================================================

# ----------------------------------------------------------------------------
# STAGE 1: Build de assets (Tailwind CSS)
# ----------------------------------------------------------------------------
FROM node:20-alpine AS assets-builder

WORKDIR /build

COPY package.json package-lock.json* ./
RUN npm ci --silent

COPY tailwind.config.js ./
COPY app/static/src/ ./app/static/src/
COPY app/templates/ ./app/templates/

RUN npm run build:css

# ----------------------------------------------------------------------------
# STAGE 2: Aplicación Python
# ----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Usuario no-root
RUN useradd --create-home --shell /bin/bash app
WORKDIR /home/app
USER app

# PATH para pip --user
ENV PATH="/home/app/.local/bin:$PATH"

# Dependencias Python
COPY --chown=app:app requirements.txt .
RUN pip install --user -r requirements.txt

# Código de la aplicación
COPY --chown=app:app app/ ./app/
COPY --chown=app:app wsgi.py ./

# Assets compilados desde stage 1
COPY --from=assets-builder --chown=app:app /build/app/static/dist/ ./app/static/dist/

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--access-logfile", "-", "wsgi:app"]
