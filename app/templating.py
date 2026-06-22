"""vibecoded: Jinja filters for serving built frontend bundles."""
import json
from functools import lru_cache
from pathlib import Path

from flask import current_app

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CANDIDATE_DIST_DIRS = [
    Path(__file__).resolve().parent / 'static' / 'dist',
    _REPO_ROOT / 'dist',
]


def _resolve_dist_dir() -> Path | None:
    for d in _CANDIDATE_DIST_DIRS:
        if (d / '.vite' / 'manifest.json').exists():
            return d
    return None


@lru_cache(maxsize=1)
def _read_manifest() -> tuple[dict, Path | None]:
    dist = _resolve_dist_dir()
    if dist is None:
        return {}, None
    path = dist / '.vite' / 'manifest.json'
    try:
        return json.loads(path.read_text()), dist
    except (OSError, json.JSONDecodeError):
        current_app.logger.warning("Frontend manifest unreadable: %s", path)
        return {}, None


def _by_name(manifest: dict) -> dict[str, dict]:
    out = {}
    for src_path, info in manifest.items():
        if isinstance(info, dict) and info.get('name'):
            out[info['name']] = info
    return out


def _shared_css(dist_dir: Path | None) -> list[str]:
    if not dist_dir:
        return []
    assets = dist_dir / 'assets'
    if not assets.exists():
        return []
    return [f'/static/dist/assets/{c.name}' for c in sorted(assets.glob('style-*.css'))]


def _resolve(manifest: dict, entry: str, seen: set | None = None) -> list[str]:
    seen = seen or set()
    if entry in seen:
        return []
    seen.add(entry)
    by_name = _by_name(manifest)
    info = by_name.get(entry) or manifest.get(f'src/js/{entry}.js')
    if not info:
        return []
    js_files = [f"/static/dist/{info['file']}"]
    for imp in info.get('imports', []):
        for k, v in manifest.items():
            if isinstance(v, dict) and v.get('file') == imp:
                imp_name = v.get('name')
                if imp_name:
                    js_files.extend(_resolve(manifest, imp_name, seen))
                break
    return js_files


def bundle(entry: str) -> str:
    manifest, dist = _read_manifest()
    js_files = _resolve(manifest, entry)
    css_files = _shared_css(dist)
    if not js_files:
        current_app.logger.warning(
            "Frontend entry '%s' not in manifest. Has `npm --prefix frontend run build` been run?",
            entry,
        )
        return (
            f"<!-- vibecoded: no bundle for '{entry}' "
            f"(run `npm --prefix frontend run build`) -->"
        )
    tags = [f'<link rel="stylesheet" href="{c}">' for c in css_files]
    tags += [f'<script type="module" src="{j}"></script>' for j in js_files]
    return '\n  '.join(tags)


def frontend_ready() -> bool:
    return _resolve_dist_dir() is not None


def register_filters(app):
    app.jinja_env.filters['bundle'] = bundle
