# Upgrading from pre-vibecoded pwnamap

The `vibecoded` branch changes **how pwnamap stores its data**. If you
have an existing install with captured handshakes, cracked networks, and
user accounts, **follow this guide once** to keep your data.

## TL;DR

```bash
cd /path/to/pwnamap          # where your docker-compose.yml lives
git pull                     # or just pull the vibecoded branch
git checkout vibecoded
./migrate-data.sh            # ONE-TIME migration of your old data
docker compose up -d         # start the new container
```

After that, your data lives in Docker's named volume `pwnamap_data` and
is managed automatically.

## What changed

| Aspect | Before (main) | After (vibecoded) |
|---|---|---|
| Python | 3.9 (EOL) | 3.12 (current) |
| Web server | Flask dev server | Gunicorn (production) |
| User | root (in container) | non-root `app` user |
| Data storage | Bind-mount on `~/.docker-data` | Named volume `pwnamap_data` |
| Image | Single Python stage | Multi-stage (Node build → Python runtime) |
| Frontend | Static files, jQuery from CDN | Vite-bundled, PWA, zero CDN |
| Test runner | None | pytest (smoke tests) |
| Linter | None | ruff |

## What does NOT change

- **Your data**: networks, handshakes, user accounts, API keys, cracked passwords.
- **The DB schema**: same SQLite tables, same column names.
- **The API**: same endpoints, same responses.
- **The plugin**: `pwnamap-plugin` keeps working without changes.

The migration is **a file copy**, not a schema migration.

## Detailed migration steps

### 1. Find your existing data

Pre-vibecoded compose had:
```yaml
volumes:
  - "${HOME}/.docker-data:/app/app/data"
```

So your DB is at `${HOME}/.docker-data/pwnamap.db` (usually
`~/.docker-data/pwnamap.db`).

If you used a different path, edit `migrate-data.sh`:
```sh
OLD_DIR="/your/custom/path"
```

### 2. Pull the new code

```bash
cd /path/to/pwnamap
git fetch origin
git checkout vibecoded
```

### 3. Run the migration script

```bash
./migrate-data.sh
```

This will:
1. Check the old DB exists at `~/.docker-data/pwnamap.db`.
2. Create the new `pwnamap_data` named volume (if not yet present).
3. Copy `pwnamap.db` into the new volume.
4. Copy `handshakes/` and `potfile/` if present.
5. Verify the copy worked.

If you prefer to see what's happening, run with `set -x`:

```bash
sh -x ./migrate-data.sh
```

### 4. Start pwnamap

```bash
docker compose up -d
docker compose logs -f pwnamap
```

You should see something like:
```
INFO DB data directory OK at /app/app/data
INFO Booting gunicorn on 0.0.0.0:1337
```

If you see a permission error, your `~/.docker-data/pwnamap.db` was owned
by `root` from the old container. Fix with:

```bash
# Run a shell in the new container
docker compose exec pwnamap sh
# Inside: chown -R app:app /app/app/data
# Or: chmod -R u+rwX /app/app/data
```

### 5. Verify

Open http://your-host:1337/ — you should see your existing data.

API check:
```bash
curl -H "X-API-KEY: $YOUR_KEY" http://your-host:1337/api/explore?network_type=WIFI | jq '.[0]'
```

## Rollback

If something goes wrong, your old data is **untouched** at
`~/.docker-data/pwnamap.db`. To roll back:

```bash
docker compose down
git checkout main
docker compose up -d
```

## Data location reference

| Path | What |
|---|---|
| `~/.docker-data/pwnamap.db` | Old: SQLite DB (pre-vibecoded) |
| `~/.docker-data/handshakes/` | Old: captured handshakes (pre-vibecoded) |
| `~/.docker-data/potfile/` | Old: uploaded potfiles (pre-vibecoded) |
| Docker volume `pwnamap_data` | New: same data, managed by Docker |

To inspect the new volume from the host:
```bash
docker volume inspect pwnamap_data
# Mountpoint is something like /var/lib/docker/volumes/pwnamap_data/_data
```

To browse files:
```bash
docker run --rm -v pwnamap_data:/data alpine:3.20 ls -la /data
```

## FAQ

**Q: Do I need to change anything in pwnamap-plugin?**
A: No. The API is unchanged.

**Q: Will my existing API key still work?**
A: Yes. The API key is stored in the DB, which is migrated.

**Q: My old container was on `jakami/pwnamap:latest` from Docker Hub. Do I still need that?**
A: No. `docker compose build` builds the image locally from your checkout.
   The Docker Hub image is the OLD pre-vibecoded code.

**Q: Can I use the same DB file across both old and new containers?**
A: Yes. The schema is unchanged. Don't run both at the same time though.

**Q: How do I update my Docker Hub deployment?**
A: Stop using the Hub image. Build locally and push to your own registry,
   or just run `docker compose` on the host directly.
