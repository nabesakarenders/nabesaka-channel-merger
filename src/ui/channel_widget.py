import os
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.core.processor import load_image
from src.core.utils import resource_path
from src.ui.elided_label import ElidedLabel


class ChannelWidget(QGroupBox):
    # Signal emitted when content changes (image loaded, value changed, channel selected)
    contentChanged = Signal()
    # Signal emitted when file is dropped (path)
    fileDropped = Signal(str)

    def __init__(self, title, color_code, parent=None):
        super().__init__(title, parent)
        self.color_code = color_code  # e.g. "R", "G", "B", "A"

        # Data
        self.current_image_path = None
        self.current_image_data = None  # numpy array
        self.is_image_mode = True  # vs Value mode

        self.init_ui()
        self.apply_styles()

    def apply_styles(self):
        # Color specific border or header maybe?
        # For now relying on main style
        pass

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Mode Selection
        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(0, 0, 0, 15)
        self.btn_image_mode = QToolButton()
        self.btn_image_mode.setText("Image")
        self.btn_image_mode.setCheckable(True)
        self.btn_value_mode = QToolButton()
        self.btn_value_mode.setText("Value")
        self.btn_value_mode.setCheckable(True)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.btn_image_mode)
        self.mode_group.addButton(self.btn_value_mode)

        self.btn_image_mode.setChecked(True)

        self.mode_group.buttonToggled.connect(self.on_mode_changed)

        mode_layout.addWidget(self.btn_image_mode)
        mode_layout.addWidget(self.btn_value_mode)
        layout.addLayout(mode_layout)

        # Image Control Area
        self.image_area = QWidget()
        image_layout = QVBoxLayout(self.image_area)
        image_layout.setContentsMargins(0, 0, 0, 15)
        image_layout.setSpacing(15)

        # File Loading
        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 15)
        self.lbl_filename = ElidedLabel("No file loaded")
        self.lbl_filename.setWordWrap(True)
        self.lbl_filename.setMaximumWidth(100)
        self.lbl_filename.setToolTip("No file loaded")
        self.btn_load = QPushButton("Load Image")
        self.btn_load.clicked.connect(self.load_file_dialog)

        file_layout.addWidget(self.lbl_filename)
        file_layout.addWidget(self.btn_load)
        image_layout.addLayout(file_layout)

        # Channel Selection
        self.combo_channel = QComboBox()
        self.combo_channel.setEnabled(False)
        self.combo_channel.currentIndexChanged.connect(
            lambda: self.contentChanged.emit()
        )

        channel_layout = QHBoxLayout()
        channel_layout.setContentsMargins(0, 0, 0, 15)
        channel_layout.addWidget(QLabel("Channel:"))
        channel_layout.addWidget(self.combo_channel)
        image_layout.addLayout(channel_layout)

        # Drop Zone (Conceptual visual)
        self.drop_label = QLabel("Drag & Drop")
        self.drop_label.setObjectName("DragDropLabel")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setMinimumHeight(200)
        self.drop_label.setMaximumHeight(200)
        # Enable drops
        self.setAcceptDrops(True)

        image_layout.addWidget(self.drop_label)

        # Thumbnail Preview
        self.lbl_thumbnail = QLabel()
        self.lbl_thumbnail.setText("Image Preview")
        self.lbl_thumbnail.setAlignment(Qt.AlignCenter)
        self.lbl_thumbnail.setMinimumHeight(200)
        self.lbl_thumbnail.setMaximumHeight(200)
        self.lbl_thumbnail.setStyleSheet(
            "background-color: #222; border: 1px solid #444; font-size: 16px; color: #777;"
        )
        self.lbl_thumbnail.setVisible(True)
        image_layout.addWidget(self.lbl_thumbnail)

        self.clear_layout = QHBoxLayout()
        self.clear_layout.setContentsMargins(0, 0, 0, 15)
        # Clear button
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setIcon(QIcon(resource_path("images/clear.svg")))
        self.btn_clear.setToolTip("Clear channel")
        self.btn_clear.setEnabled(False)
        self.btn_clear.clicked.connect(self.clear_image)
        self.clear_layout.addWidget(self.btn_clear)

        image_layout.addLayout(self.clear_layout)

        layout.addWidget(self.image_area)

        # Value Control Area
        self.value_area = QWidget()
        value_layout = QVBoxLayout(self.value_area)
        value_layout.setContentsMargins(0, 0, 0, 0)

        val_controls = QHBoxLayout()
        self.slider_val = QSlider(Qt.Horizontal)
        self.slider_val.setRange(0, 255)
        # Default values based on color code?
        default_val = 255 if self.color_code == "A" else 0
        self.slider_val.setValue(default_val)

        self.spin_val = QSpinBox()
        self.spin_val.setRange(0, 255)
        self.spin_val.setValue(default_val)

        self.value_preview = QFrame()
        self.value_preview.setFixedSize(32, 32)
        self.value_preview.setFrameShape(QFrame.Box)
        self.value_preview.setLineWidth(1)
        self.value_preview.setStyleSheet(
            f"background-color: rgb({default_val}, {default_val}, {default_val});"
        )

        # Sync slider and spin
        self.slider_val.valueChanged.connect(self.spin_val.setValue)
        self.spin_val.valueChanged.connect(self.slider_val.setValue)
        self.slider_val.valueChanged.connect(self.update_value_preview)
        self.spin_val.valueChanged.connect(self.update_value_preview)
        self.slider_val.valueChanged.connect(lambda: self.contentChanged.emit())
        self.spin_val.valueChanged.connect(lambda: self.contentChanged.emit())

        val_controls.addWidget(self.slider_val)
        val_controls.addWidget(self.spin_val)
        val_controls.addWidget(self.value_preview)
        value_layout.addLayout(val_controls)

        layout.addWidget(self.value_area)

        layout.addStretch()

        self.update_ui_state()

    def clear_image(self):
        self.current_image_path = None
        self.current_image_data = None
        self.btn_clear.setEnabled(False)
        self.lbl_filename.setFullText("No file loaded")
        self.lbl_filename.setToolTip("No file loaded")
        self.lbl_thumbnail.clear()
        self.combo_channel.clear()
        self.combo_channel.setEnabled(False)
        self.contentChanged.emit()

    def update_value_preview(self, value):
        self.value_preview.setStyleSheet(
            f"background-color: rgb({value}, {value}, {value});"
        )

    def update_ui_state(self):
        self.is_image_mode = self.btn_image_mode.isChecked()
        self.image_area.setVisible(self.is_image_mode)
        self.value_area.setVisible(not self.is_image_mode)
        self.contentChanged.emit()

    def on_mode_changed(self, btn, checked):
        if checked:
            self.update_ui_state()

    def load_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            self.window().last_directory,
            "Images (*.png *.jpg *.jpeg *.tga *.bmp *.exr *.tif *.tiff)",
        )
        if path:
            self.window().last_directory = str(Path(path).parent)
            self.load_image_from_path(path)
            self.fileDropped.emit(path)  # We should handle smart loading here too

    def load_image_from_path(self, path):
        self.current_image_path = path
        self.lbl_filename.setFullText(os.path.basename(path))
        self.lbl_filename.setToolTip(os.path.basename(path))

        # Load data to inspect channels
        img = load_image(path)
        if img is not None:
            self.current_image_data = img
            self.populate_channel_combo(img)
            self.btn_clear.setEnabled(True)

            # Generate Thumbnail
            self.update_thumbnail(img)

            self.contentChanged.emit()
        else:
            self.lbl_filename.setFullText("Error loading file")
            self.lbl_filename.setToolTip("Error loading file")
            self.current_image_data = None
            self.combo_channel.clear()
            self.combo_channel.setEnabled(False)
            self.lbl_thumbnail.setVisible(False)

    def update_thumbnail(self, img_data):
        from PySide6.QtGui import QImage, QPixmap

        from src.core.processor import normalize_to_8bit

        try:
            # Normalize for display
            if img_data.dtype == np.uint16:
                disp_data = normalize_to_8bit(img_data)
            else:
                disp_data = img_data.astype(np.uint8)

            h, w = disp_data.shape[:2]

            # Handle Grayscale vs RGB vs RGBA
            if disp_data.ndim == 2:
                # Grayscale
                fmt = QImage.Format_Grayscale8
                bytes_per_line = w
                q_img = QImage(disp_data.data, w, h, bytes_per_line, fmt)
            else:
                channels = disp_data.shape[2]
                bytes_per_line = w * channels
                if channels == 3:
                    fmt = QImage.Format_RGB888
                elif channels == 4:
                    fmt = QImage.Format_RGBA8888
                else:
                    return  # Unknown

                q_img = QImage(disp_data.data, w, h, bytes_per_line, fmt)

            pix = QPixmap.fromImage(q_img)
            scaled = pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_thumbnail.setPixmap(scaled)
            self.lbl_thumbnail.setVisible(True)
        except Exception as e:
            print(f"Thumbnail error: {e}")
            self.lbl_thumbnail.setVisible(False)

    def populate_channel_combo(self, img_data):
        self.combo_channel.blockSignals(True)
        self.combo_channel.clear()

        if img_data.ndim == 2:
            self.combo_channel.addItem("Gray / Lightness", 0)
        else:
            channels = img_data.shape[2]
            names = ["Red", "Green", "Blue", "Alpha"]
            for i in range(channels):
                name = names[i] if i < 4 else f"Channel {i}"
                self.combo_channel.addItem(name, i)

        # Auto-select based on color_code if possible (Smart Select)
        target_idx = -1
        if self.color_code == "R":
            target_idx = 0
        elif self.color_code == "G":
            target_idx = 1
        elif self.color_code == "B":
            target_idx = 2
        elif self.color_code == "A":
            target_idx = 3

        # If image lacks the target channel (e.g. asking for Alpha in RGB), default to Red (0) or Gray
        if target_idx >= self.combo_channel.count():
            target_idx = 0

        self.combo_channel.setCurrentIndex(target_idx)
        self.combo_channel.setEnabled(True)
        self.combo_channel.blockSignals(False)

    def get_data(self):
        """
        Returns the data for this channel.
        Can be an int (value mode) or image numpy array (image mode).
        If image mode but no image loaded, returns None (usually treated as 0).
        Actually, let's return a tuple (type, data) or just the raw input expected by processor.ui usage.

        Processor expects: array or int or None.

        If Image Mode:
            Returns: numpy array of the specific single channel.
        If Value Mode:
            Returns: int value.
        """
        if not self.is_image_mode:
            return self.spin_val.value()

        if self.current_image_data is None:
            return None

        # Extract channel
        idx = self.combo_channel.currentData()
        if idx is None:
            return None

        # We need to extract the slice here?
        # Processor's merge_channels helper expects SINGLE CHANNEL arrays or ints.
        # So we should slice it here using processor helper
        from src.core.processor import get_channel_data

        return get_channel_data(self.current_image_data, idx)

    # Drag and Drop events
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            if files:
                path = files[0]
                # If we want to support global "Smart Load", we might bubble this up?
                # But here we are dropping ONTO the specific widget.
                # Requirement: "If an RGB image is drag/dropped it should load it into the R G and B channel slots"
                # This suggests global behavior.
                # But user might also drop specific image to specific channel.
                # Let's emit a signal and let MainWindow decide if it should populate others?
                # Or just load here?
                # "Detect if the loaded image has multiple channels... allow selection"

                # I'll emit fileDropped and load it locally.
                # Main Window can intercept fileDropped from this widget if it wants to do magic.
                self.load_image_from_path(path)
                self.fileDropped.emit(path)
