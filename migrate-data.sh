#!/bin/sh
# vibecoded: migrate pwnamap.db from pre-vibecoded install to new named volume.
#
# Pre-vibecoded: data lived at $HOME/.docker-data/pwnamap.db (bind-mounted)
# Post-vibecoded: data lives in the Docker named volume `pwnamap_data`.
#
# Run this ONCE after upgrading your compose file, BEFORE starting pwnamap.
# Safe to re-run -- it's a copy, not a move.

set -e

OLD_DIR="${HOME}/.docker-data"
OLD_DB="${OLD_DIR}/pwnamap.db"
NEW_VOLUME="pwnamap_data"

echo "==> pwnamap data migration"
echo

# 1. Check the old DB exists
if [ ! -f "$OLD_DB" ]; then
  echo "No existing database found at $OLD_DB"
  echo "Nothing to migrate. If this is a fresh install, you can ignore this script."
  exit 0
fi

echo "Found existing database: $OLD_DB"
ls -la "$OLD_DB"
echo

# 2. Find a container using the new named volume (if already created)
CONTAINER=$(docker ps -a --filter "volume=${NEW_VOLUME}" --format "{{.Names}}" | head -1)
if [ -z "$CONTAINER" ]; then
  # Maybe the volume exists but no container is using it yet
  if ! docker volume inspect "$NEW_VOLUME" >/dev/null 2>&1; then
    echo "Creating named volume $NEW_VOLUME..."
    docker volume create "$NEW_VOLUME"
  fi

  echo "No running pwnamap container found. Copying via a temporary container..."
  docker run --rm \
    -v "${NEW_VOLUME}:/target" \
    -v "${OLD_DIR}:/source:ro" \
    alpine:3.20 \
    sh -c "cp -av /source/pwnamap.db /target/ && \
           [ -d /source/handshakes ] && cp -rav /source/handshakes /target/ || true && \
           [ -d /source/potfile ] && cp -rav /source/potfile /target/ || true"
else
  echo "Found pwnamap container: $CONTAINER"
  echo "Copying into the container's /app/app/data/ ..."
  docker cp "$OLD_DIR/." "${CONTAINER}:/app/app/data/"
fi

echo
echo "==> Migration complete!"
echo
echo "Verifying:"
docker run --rm \
  -v "${NEW_VOLUME}:/target" \
  alpine:3.20 \
  sh -c "ls -la /target/ && echo --- && [ -f /target/pwnamap.db ] && echo 'pwnamap.db OK'"
echo
echo "You can now start pwnamap:  docker compose up -d"
