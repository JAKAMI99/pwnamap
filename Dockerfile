# vibecoded: multi-stage build — Node builds the frontend bundle, Python serves it.
# Runtime image contains zero Node, zero npm — only the prebuilt static assets.

# ============ Stage 1: Frontend bundle ============
FROM node:22-alpine AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund 2>/dev/null \
    || npm install --no-audit --no-fund

COPY frontend/vite.config.js ./
COPY frontend/src ./src

RUN npm run build

# ============ Stage 2: Python runtime ============
FROM python:3.12-alpine

ENV APP_VERSION="0.9.0" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    PORT=1337

RUN apk add --no-cache \
        build-base \
        curl \
        tini

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python app source
COPY app/ ./app/
COPY run.py ./

# vibecoded: copy prebuilt frontend bundle (Vite wrote to /build/dist/)
COPY --from=frontend-builder /build/dist /app/static/dist

# vibecoded: run as non-root for defense in depth
RUN addgroup -S app && adduser -S app -G app \
    && chown -R app:app /app
USER app

EXPOSE 1337

# vibecoded: tini for proper signal forwarding, gunicorn instead of flask dev server
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["gunicorn", "--bind", "0.0.0.0:1337", "--workers", "2", "--threads", "4", \
     "--access-logfile", "-", "--error-logfile", "-", \
     "run:app"]
