# AGENTS.md

Guidelines for agentic coding agents working in this repository.

## Project Overview

Texture Channel Merger is a desktop GUI application for combining image channels (R, G, B, A) from separate source images into a single output texture. Built with Python using PySide6 (Qt), NumPy, and OpenCV.

## Commands

### Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Run from project root
python src/main.py
```

### Testing

```bash
# Run all tests
python test_processor.py

# Run a single test function
python -c "from test_processor import test_merge_logic; test_merge_logic()"
```

### Building (PyInstaller)

```bash
# Windows build
pyinstaller --noconfirm --onefile --windowed --name "ChannelMerger" --icon "assets/images/app_icon.ico" --add-data "assets;assets" --paths "." --clean src/main.py

# Linux build
pyinstaller --noconfirm --onefile --windowed --name "ChannelMerger" --icon "assets/images/app_icon.ico" --add-data "assets:assets" --paths "." --clean src/main.py

# Or use the existing spec file
pyinstaller ChannelMerger.spec
```

### Linting

No linting tools are currently configured. Consider installing and using:
```bash
pip install ruff
ruff check src/
```

## Project Structure

```
ChannelMerger/
├── src/
│   ├── main.py              # Application entry point
│   ├── core/
│   │   └── processor.py     # Image processing functions
│   └── ui/
│       ├── main_window.py   # Main application window
│       ├── channel_widget.py # Channel input widgets
│       └── styles.py        # QSS stylesheet constants
├── assets/
│   ├── images/              # Icons and app assets
│   └── sounds/              # Audio feedback sounds
├── test_processor.py        # Unit tests for processor module
├── requirements.txt         # Python dependencies
└── ChannelMerger.spec       # PyInstaller spec file
```

## Code Style Guidelines

### Imports

Order imports as follows, separated by blank lines:
1. Standard library imports (alphabetically)
2. Third-party imports (alphabetically)
3. Local imports (alphabetically)

```python
import os
import sys

import numpy as np
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.core.processor import load_image
from src.ui.styles import DARK_THEME
```

### Naming Conventions

- **Functions**: `snake_case` (e.g., `load_image`, `merge_channels`)
- **Variables**: `snake_case` (e.g., `current_image_path`, `target_shape`)
- **Classes**: `PascalCase` (e.g., `ChannelWidget`, `MainWindow`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DARK_THEME`)
- **Private methods**: Prefix with underscore (e.g., `_internal_helper`)
- **Signals (Qt)**: `camelCase` with descriptive names (e.g., `contentChanged`, `fileDropped`)

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: ~100 characters
- Blank lines between logical sections
- No trailing whitespace

### Documentation

Use docstrings for all public functions and classes:

```python
def load_image(file_path):
    """
    Loads an image from the file path using OpenCV.
    Returns a numpy array in RGB/RGBA format.
    """
```

### Error Handling

- Use try/except blocks for operations that may fail (file I/O, image processing)
- Print error messages with context: `print(f"Error loading image {file_path}: {e}")`
- Return `None` or `False` on failure for graceful degradation
- Never silently catch exceptions without handling or logging

```python
def save_image(path, data):
    try:
        # ... operation ...
        return success
    except Exception as e:
        print(f"Error saving image to {path}: {e}")
        return False
```

### Type Hints

Type hints are optional but encouraged for function signatures:

```python
def get_channel_data(image_data: np.ndarray, channel_index: int) -> np.ndarray | None:
```

### Qt/PySide6 Patterns

- Signal connections: Use lambda for simple callbacks, methods for complex logic
- Block signals when programmatically updating widgets: `widget.blockSignals(True)` / `widget.blockSignals(False)`
- Use `QTimer` for debounced UI updates
- Apply styles via `setStyleSheet()` using constants from `styles.py`

### NumPy/OpenCV Patterns

- Use `cv2.IMREAD_UNCHANGED` to preserve bit depth and channels
- OpenCV uses BGR; convert to RGB for internal processing: `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`
- Check `dtype` before operations: `if img.dtype == np.uint16:`
- Use `np.dstack()` for channel merging

### File Paths

- Use `pathlib.Path` for cross-platform path handling
- Handle frozen (PyInstaller) vs development paths:

```python
if getattr(sys, 'frozen', False):
    assets_path = Path(sys._MEIPASS) / "assets"
else:
    assets_path = Path(__file__).resolve().parent.parent.parent / "assets"
```

### Testing

- Place tests in the project root
- Import from `src.` namespace after adding project root to path
- Use simple assert statements for validation
- Clean up test artifacts in try/except blocks
