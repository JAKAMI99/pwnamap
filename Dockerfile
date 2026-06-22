# vibecoded: modernisiert — Python 3.9 → 3.12, non-root, gunicorn
FROM python:3.12-alpine

ENV APP_VERSION="0.9.0" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    PORT=1337

# Build deps for bcrypt + runtime deps for healthcheck + tini for signal handling
RUN apk add --no-cache \
        build-base \
        curl \
        tini

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

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
