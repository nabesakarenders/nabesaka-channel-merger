import os
import sys
from pathlib import Path


def resource_path(relative_path):
    """Resolve path to a bundled resource, works both in dev and PyInstaller."""
    if getattr(sys, "frozen", False):
        assets_path = Path(sys._MEIPASS) / "assets"
    else:
        assets_path = Path(__file__).resolve().parent.parent.parent / "assets"
    return os.path.join(assets_path, relative_path)
