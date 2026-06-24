"""vibecoded: minimal launcher.

Production (gunicorn):
    gunicorn run:app

Development (Flask dev server):
    python run.py

First-time local setup:
    python dev.py        # creates venv, installs deps, builds frontend
    python run.py        # starts the app

Container (Dockerfile):
    CMD ["gunicorn", "--bind", "0.0.0.0:1337", ...]
    -- no init step, the Dockerfile builds the frontend in stage 1.
"""
from app import create_app

app = create_app()


if __name__ == "__main__":
    # Dev server only. In production, gunicorn imports `app` directly.
    app.run(host="0.0.0.0", port=1337, debug=True)
