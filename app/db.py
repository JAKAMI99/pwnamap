"""vibecoded: central DB path resolution.

Originally every route hardcoded 'app/data/pwnamap.db'. This module gives
one place to read DATA_DIR and to open a connection with the standard
row factory.

Resolution order (highest priority first):
  1. DATA_DIR environment variable
  2. Flask app.config["DATA_DIR"] (set by tests via create_app({"DATA_DIR": ...}))
  3. Default "app/data" (relative to app package or CWD)

Usage:
    from app.db import get_db
    conn = get_db()
    cursor = conn.execute(...)
"""
import logging
import os
import sqlite3

log = logging.getLogger(__name__)

# vibecoded: env-driven so docker-compose / k8s / bare-metal all work.
# This is the FALLBACK used only when neither env nor config is set.
DEFAULT_DATA_DIR = "app/data"
DB_FILENAME = "pwnamap.db"


def resolve_data_dir() -> str:
    """Return the effective data directory."""
    env_val = os.environ.get("DATA_DIR")
    if env_val:
        return env_val
    try:
        from flask import current_app
        cfg_val = current_app.config.get("DATA_DIR")
        if cfg_val:
            return cfg_val
    except RuntimeError:
        # No Flask app context -- fall through to default.
        pass
    return DEFAULT_DATA_DIR


def db_path() -> str:
    """Return absolute path to the SQLite DB file.

    Relative paths are resolved against the Flask app's root_path (or CWD
    if no app context). Inside the Docker container, "app/data" thus
    becomes "/app/app/data" -- matching the volume mount target.
    """
    data_dir = resolve_data_dir()
    if os.path.isabs(data_dir):
        return os.path.join(data_dir, DB_FILENAME)
    # vibecoded: resolve relative paths against the app package directory.
    try:
        from flask import current_app
        base = current_app.root_path
    except RuntimeError:
        # No app context -- assume CWD is the project root (gunicorn sets it).
        base = os.getcwd()
    return os.path.join(base, data_dir, DB_FILENAME)


def ensure_data_dir() -> str:
    """Create the data directory if missing, return its path."""
    path = os.path.dirname(db_path())
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        log.info("Created data directory at %s", path)
    return path


def get_db() -> sqlite3.Connection:
    """Open a connection to the DB. Caller is responsible for closing."""
    ensure_data_dir()
    path = db_path()
    log.debug("Opening SQLite DB at %s", path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def check_writable() -> None:
    """Fail fast if the DB directory is not writable.

    Called at app startup so misconfigured deployments surface immediately
    rather than 500-ing on the first request.
    """
    path = ensure_data_dir()
    test_file = os.path.join(path, ".write_test")
    try:
        with open(test_file, "w") as f:
            f.write("ok")
        os.unlink(test_file)
    except OSError as exc:
        log.fatal("Cannot write to data directory %s: %s", path, exc)
        raise PermissionError(
            f"Data directory {path} is not writable: {exc}"
        ) from exc
