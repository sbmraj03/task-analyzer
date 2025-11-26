from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


FRONTEND_ROOT = (Path(settings.BASE_DIR).parent / 'frontend').resolve()


def _resolve_frontend_file(relative_path: str) -> Path:
    """Return an absolute path within the frontend bundle."""
    target = (FRONTEND_ROOT / relative_path).resolve()
    if not FRONTEND_ROOT.exists() or not target.is_file() or FRONTEND_ROOT not in target.parents:
        raise Http404("Requested frontend asset is not available.")
    return target


def frontend_index(request):
    """Serve the SPA's entry point for the root path."""
    index_file = _resolve_frontend_file('index.html')
    return FileResponse(index_file.open('rb'))


def frontend_asset(request, asset_path: str):
    """Serve CSS/JS assets that live next to index.html during development."""
    asset_file = _resolve_frontend_file(asset_path)
    return FileResponse(asset_file.open('rb'))

