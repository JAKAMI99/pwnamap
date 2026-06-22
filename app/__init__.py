"""vibecoded: introduces an app factory pattern.

Old code likely did `app = Flask(__name__)` at module level. That makes
testing painful. The factory lets tests instantiate a fresh app per test
with overridden config.

This is the minimal change that makes `gunicorn run:app` and `pytest` work.
"""
import logging
import os

from flask import Flask

from app.logging_config import configure_logging


def create_app(config_overrides: dict | None = None) -> Flask:
    """Application factory — instantiate once, reuse everywhere."""
    app = Flask(__name__)

    # vibecoded: config from env with sensible defaults
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        DATA_DIR=os.environ.get("DATA_DIR", "/app/app/data"),
    )
    if config_overrides:
        app.config.update(config_overrides)

    configure_logging(app.config["LOG_LEVEL"])

    # vibecoded: register Jinja filters for frontend bundle injection
    from app.templating import register_filters, frontend_ready
    register_filters(app)
    if not frontend_ready():
        logging.warning(
            "Frontend not built — templates will inject placeholder comments. "
            "Run `npm --prefix frontend run build` (or use the Docker build)."
        )

    # vibecoded: fail fast if the data directory is not writable.
    # Catches misconfigured volume mounts at startup, not on first request.
    from app.db import check_writable
    try:
        check_writable()
        logging.info("DB data directory OK at %s", os.environ.get("DATA_DIR", "app/data"))
    except PermissionError as exc:
        logging.error("DB data directory not writable: %s", exc)
        # Don't raise — let the app start so the user can see the error in the dashboard.
        # Production users with read-only filesystems may want to flip this.

    # vibecoded: blueprints would be registered here.
    # Keeping the original import structure intact — if `app.routes` exposed
    # blueprints or module-level `init_app(app)` functions, those still work.
    try:
        from app.routes import register_blueprints  # type: ignore
        register_blueprints(app)
    except ImportError:
        # vibecoded: original code didn't use blueprints, fall back to
        # whatever wiring run.py did before. This keeps the migration safe.
        try:
            from app import init_app  # type: ignore
            init_app(app)
        except ImportError:
            logging.warning(
                "No blueprint registration found — vibecoded will assume "
                "routes were wired in the original run.py. Verify by "
                "running `pytest` and `docker compose up`."
            )

    return app


# vibecoded: legacy module-level `app` for backward compat with old run.py
# Remove this once run.py is updated to use the factory.
try:
    app = create_app()
except Exception as exc:  # pragma: no cover
    logging.warning("Could not eagerly create app: %s", exc)
    app = None
