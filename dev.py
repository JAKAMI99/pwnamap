#!/usr/bin/env python3
"""vibecoded: LOCAL DEV SETUP. NOT used in Docker.

This script is for getting a fresh checkout running on a developer
laptop. The Dockerfile does all this automatically in its build stage,
so do NOT run this in containers.

Usage:
    python dev.py              # full setup (idempotent, safe to re-run)
    python dev.py --no-frontend  # skip frontend build
    python dev.py --no-venv      # install deps system-wide (not recommended)

What it does:
    1. Creates .venv/ and installs requirements.txt
    2. Runs `npm install` and `npm run build` in frontend/
    3. Copies the build output to app/static/dist/
    4. Creates app/data/ if missing
    5. Prints next-step hints

Prerequisites:
    - Python 3.10+
    - Node.js 18+ (for the frontend build)
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
DATA_DIR = ROOT / "app" / "data"
DIST_DIR = ROOT / "app" / "static" / "dist"
FRONTEND_DIR = ROOT / "frontend"

SKIP_FRONTEND = "--no-frontend" in sys.argv
SKIP_VENV = "--no-venv" in sys.argv


def step(label):
    """Print a section header."""
    print()
    print(">>> " + label)


def run(cmd, **kwargs):
    """Run a subprocess, streaming output."""
    print("  $ " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, **kwargs)


def venv_python():
    if sys.platform == "win32":
        candidate = VENV / "Scripts" / "python.exe"
    else:
        candidate = VENV / "bin" / "python"
    return candidate if candidate.exists() else None


def setup_venv():
    py = venv_python()
    if py is None:
        step("Creating venv")
        run([sys.executable, "-m", "venv", str(VENV)], check=True)
        py = venv_python()
    else:
        step("Using existing venv at " + str(py))

    step("Installing Python deps")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    run([str(py), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], check=True)
    print("  Done.")
    return py


def setup_frontend():
    if SKIP_FRONTEND:
        print()
        print(">>> Skipping frontend (--no-frontend)")
        return False
    if not FRONTEND_DIR.exists():
        print()
        print(">>> frontend/ not found, skipping frontend")
        return False
    if not shutil.which("npm"):
        print()
        print(">>> npm not in PATH. Install Node.js 18+ then re-run.")
        print("    https://nodejs.org/")
        return False

    if not (FRONTEND_DIR / "node_modules").exists():
        step("npm install")
        run(["npm", "install", "--no-audit", "--no-fund"], cwd=str(FRONTEND_DIR), check=True)

    step("npm run build")
    run(["npm", "run", "build"], cwd=str(FRONTEND_DIR), check=True)

    build_out = ROOT / "dist"
    if not build_out.exists():
        print("  WARNING: expected build output at " + str(build_out))
        return False
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    shutil.copytree(build_out, DIST_DIR)
    print("  Bundle copied to " + str(DIST_DIR))
    return True


def setup_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print()
    print(">>> Data dir at " + str(DATA_DIR))


def print_next_steps():
    print()
    print("=" * 60)
    print("Setup complete. Next steps:")
    print("=" * 60)
    print()
    print("  1. Drop your existing DB into app/data/pwnamap.db")
    print("     (or run python run.py without one to go through the")
    print("      first-run setup wizard)")
    print()
    print("  2. Start the app:")
    print("     python run.py")
    print()
    print("  3. Open http://localhost:1337 in your browser.")
    print()
    print("If you have an old Docker-based install, see MIGRATION.md")
    print("for upgrading without losing data.")


def main():
    print("=" * 60)
    print("pwnamap local dev setup")
    print("=" * 60)
    print("  Python: " + sys.executable)
    print("  CWD:    " + str(ROOT))

    if not SKIP_VENV:
        setup_venv()
    else:
        print()
        print(">>> Skipping venv (--no-venv); assuming deps installed system-wide")

    setup_data_dir()
    setup_frontend()
    print_next_steps()
    return 0


if __name__ == "__main__":
    sys.exit(main())
