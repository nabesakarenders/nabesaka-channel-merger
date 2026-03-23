
DARK_THEME = """
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}

QGroupBox {
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    margin-top: 20px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
    color: #a0a0a0;
}

QToolButton {
    padding: 6px 12px;
    border: 1px solid #555;
    border-radius: 4px;
    background: #2b2b2b;
}

QToolButton:checked {
    background: #3d6dcc;
    border-color: #3d6dcc;
}

QToolButton + QToolButton {
    margin-left: 4px;
}

QPushButton {
    background-color: #3e3e3e;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 5px 15px;
}

QPushButton:disabled {
    background: #333;
    color: #777;
    border-color: #444;
}

QPushButton:hover {
    background-color: #4e4e4e;
}

QPushButton:pressed {
    background-color: #2e2e2e;
}

QLineEdit {
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: 4px;
    color: #fff;
}

QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: 4px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    selection-background-color: #3e3e3e;
    color: #e0e0e0;
}

QSlider::groove:horizontal {
    border: 1px solid #3e3e3e;
    height: 8px;
    background: #1e1e1e;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #5c85d6;
    border: 1px solid #5c85d6;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #7ca1f2;
}

QLabel#DragDropLabel {
    border: 2px dashed #555;
    border-radius: 8px;
    color: #888;
    background-color: #252525;
}

QLabel#DragDropLabel:hover {
    border-color: #777;
    background-color: #2a2a2a;
}

QStatusBar {
    background-color: #222;
    color: #ccc;
    border-top: 1px solid #3e3e3e;
}

QStatusBar::item {
    border: none;
}
"""
