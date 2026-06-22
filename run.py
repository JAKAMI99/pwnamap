"""vibecoded: gunicorn-compatible entry point.

`gunicorn run:app` looks up the symbol `app` in this module.
For dev, you can still run `python run.py`.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337)
