# Lokal testen — Anleitung für dich (Jannic)

Du willst mit deiner echten `pwnamap.db` testen. Hier ist der sichere Pfad.

## Wichtig: Was wir lokal NICHT haben

Ich in meinem Hermes-Container habe **keine** echte `pwnamap.db`. Die musst du
selbst rüberkopieren. Dafür gibt es zwei Wege:

### A) DB via SCP/rsync vom Unraid in den Container

Im **Hermes-Agent-Terminal auf deinem Unraid**:

```bash
# 1. Finde deine DB
ls -la ~/.docker-data/pwnamap.db

# 2. In den Hermes-Container kopieren (vom Host aus)
docker cp ~/.docker-data/pwnamap.db Hermes-Agent:/home/hermes/.hermes/work/pwnamap/app/data/

# 3. Im Container: Rechte fixen
docker exec Hermes-Agent chown 10000:10000 \
  /home/hermes/.hermes/work/pwnamap/app/data/pwnamap.db
```

### B) DB in den neuen Docker-Volume mounten

```bash
# 1. Neue DB rüberkopieren in den Volume
docker run --rm \
  -v pwnamap_data:/data \
  -v ~/.docker-data:/source:ro \
  alpine:3.20 cp /source/pwnamap.db /data/
```

Das ist was `migrate-data.sh` macht — kannst du auch direkt aufrufen.

## Test-Szenarien

### Szenario 1: Nur die App starten (ohne DB-Migration)

```bash
# In deinem Hermes-Terminal:
cd /home/hermes/.hermes/work/pwnamap

# Frontend bauen
cd frontend
npm install
npm run build
cd ..

# Backend-Deps installieren
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# DB-Pfad setzen
export DATA_DIR=/home/hermes/.hermes/work/pwnamap/app/data

# Falls du DB aus A) hast: sollte unter app/data/pwnamap.db liegen
ls -la app/data/

# Starten
python run.py
# -> http://localhost:1337 (im Browser des Containers oder Port-Forward)
```

### Szenario 2: Mit Docker Compose (production-näher)

```bash
cd /home/hermes/.hermes/work/pwnamap

# .env-Datei erstellen
cp .env.example .env 2>/dev/null || cat > .env <<EOF
# Wigle API key (optional, leer lassen wenn nicht genutzt)
WIGLE_API_KEY=
WPASEC_API_KEY=
EOF

# Frontend bauen (im Dockerfile automatisch, aber für Dev:
cd frontend && npm run build && cd ..

# Starten
docker compose build
docker compose up

# Im Browser (von deinem Rechner, mit Port-Forward):
# http://<unraid-host>:1337
```

### Szenario 3: Tests laufen lassen

```bash
cd /home/hermes/.hermes/work/pwnamap

# Smoke-Tests (brauchen keine DB)
pytest tests/ -v

# Mit deiner DB
DATA_DIR=/path/to/your/data pytest tests/ -v

# Ruff-Linter
ruff check .

# Type-Check
mypy app/
```

### Szenario 4: DB-Migration simulieren

```bash
cd /home/hermes/.hermes/work/pwnamap

# Sicher dir erst deine alte DB!
cp ~/.docker-data/pwnamap.db ~/.docker-data/pwnamap.db.backup

# Migration laufen lassen
./migrate-data.sh

# Verifizieren
docker run --rm -v pwnamap_data:/data alpine:3.20 ls -la /data
docker run --rm -v pwnamap_data:/data alpine:3.20 sqlite3 /data/pwnamap.db ".tables"
```

## Wenn was schiefgeht

### Symptom: "Cannot write to /app/app/data"

Container-User `app` darf nicht schreiben. Fix:

```bash
docker compose exec pwnamap chown -R app:app /app/app/data
```

Oder beim alten `root`-owned DB-File:

```bash
docker run --rm -v pwnamap_data:/data alpine:3.20 \
  chown -R 10000:10000 /data
```

### Symptom: "Database is locked"

Andere Instanz läuft noch. Check:

```bash
docker ps | grep pwnamap
docker compose down
```

### Symptom: Frontend lädt nicht / 404 auf /static/dist/

Build fehlt:

```bash
cd /home/hermes/.hermes/work/pwnamap/frontend
npm run build
```

### Symptom: Pwnamap-plugin verbindet nicht mehr

API-Key hat sich nicht geändert (ist in der DB). Falls der pwnagotchi den
Hostnamen nicht mehr auflöst: check ob dein DNS noch stimmt.

## Rollback

Falls du zurück willst:

```bash
cd /home/hermes/.hermes/work/pwnamap
git checkout main  # oder dev
docker compose build
docker compose up -d
```

Deine alte DB liegt unter `~/.docker-data/pwnamap.db` — unverändert.

## Bekannte Limitierungen

- **Issue #17** ist noch offen (Diagnostic-Issue). Token hat keine Issues:write.
  Du musst es manuell im Browser schließen oder mir Bescheid geben.
- **CI-Workflow** (`ci.yml`) noch nicht committet. Token hatte keinen `workflow`-Scope.
  Manuell testen stattdessen (pytest, ruff, mypy).
- **docker-image.yml** gelöscht in Commit 1. Entscheiden: restaurieren oder weg lassen?
