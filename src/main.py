## Texture Channel Merger
# Version 0.1.3
# Author: Nabesaka
# License: MIT

import sys
import os

# Add project root to sys.path to allow 'src' imports checking first
# logical parent of src/main.py is src, parent of src is root.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication, QStyleFactory
from src.ui.main_window import MainWindow

def main():
    # Setup high DPI scaling
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    # Get the desktop environment and set to KDE if detected as such
    desktop = os.environ.get("XDG_CURRENT_DESKTOP")
    if desktop and "KDE" in desktop:
        os.environ["QT_QPA_PLATFORMTHEME"] = "xdgdesktopportal"
    
    app = QApplication(sys.argv)
    app.setApplicationName("Texture Channel Merger")
    app.setOrganizationName("Nabesaka")
    app.setOrganizationDomain("nabesaka.com")
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
