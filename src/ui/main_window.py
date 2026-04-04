import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.processor import (
    get_save_file_filter,
    merge_channels,
    normalize_to_8bit,
    save_image,
)
from src.ui.channel_widget import ChannelWidget
from src.ui.styles import DARK_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texture Channel Merger")
        self.resize(1280, 720)

        # resolve path for assets based on if we are frozen or not
        if getattr(sys, "frozen", False):
            assets_path = Path(sys._MEIPASS) / "assets"
        else:
            assets_path = Path(__file__).resolve().parent.parent.parent / "assets"

        # Add app icon
        self.setWindowIcon(QIcon(str(assets_path / "images" / "app_icon.png")))

        # Create sound effects
        self.success_sound = QSoundEffect()
        self.success_sound.setSource(
            QUrl.fromLocalFile(assets_path / "sounds" / "success.wav")
        )
        self.success_sound.setVolume(0.5)

        self.error_sound = QSoundEffect()
        self.error_sound.setSource(
            QUrl.fromLocalFile(assets_path / "sounds" / "error.wav")
        )
        self.error_sound.setVolume(0.5)

        # Store a 'last directory' for file dialogs
        self.last_directory = str(Path.home())

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(20)

        # 1. Channels Area (Left)
        # Using a ScrollArea just in case, though 4 columns should fit
        # logic: 4 widgets
        self.channels_layout = QHBoxLayout()
        self.channels_layout.setSpacing(10)

        self.widget_r = ChannelWidget("Red Output", "R")
        self.widget_g = ChannelWidget("Green Output", "G")
        self.widget_b = ChannelWidget("Blue Output", "B")
        self.widget_a = ChannelWidget("Alpha Output", "A")

        # Connect signals
        self.channels = [self.widget_r, self.widget_g, self.widget_b, self.widget_a]
        for w in self.channels:
            w.contentChanged.connect(self.request_preview_update)
            w.fileDropped.connect(self.handle_smart_load)
            w.setFixedWidth(300)
            self.channels_layout.addWidget(w)

        self.main_layout.addLayout(self.channels_layout, stretch=2)

        # 2. Separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

        # 3. Preview Area (Right)
        self.preview_layout = QVBoxLayout()

        self.lbl_preview = QLabel("Preview")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet(
            "background-color: #1a1a1a; border: 1px solid #333;"
        )
        self.lbl_preview.setMinimumSize(300, 300)
        # Scaling
        self.lbl_preview.setScaledContents(True)  # This might distort aspect ratio?
        # Better to scale pixmap manually in update
        self.lbl_preview.setScaledContents(False)

        # Bit depth selection
        self.cmb_bit_depth = QComboBox()
        self.cmb_bit_depth.addItems(
            ["Auto (Detect from Input)", "8-bit", "16-bit", "32-bit (EXR/HDR)"]
        )
        self.cmb_bit_depth.setToolTip(
            "Select output bit depth:\n"
            "• Auto: Uses highest bit depth from input channels\n"
            "• 8-bit: Standard PNG/JPEG (0-255)\n"
            "• 16-bit: High quality PNG/TIFF (0-65535)\n"
            "• 32-bit: HDR EXR/TIFF (0.0-1.0+ float)"
        )

        self.btn_export = QPushButton("Export Merged Texture")
        self.btn_export.setMinimumHeight(50)
        self.btn_export.setStyleSheet(
            "background-color: #2c5d3f; font-weight: bold; font-size: 16px;"
        )
        self.btn_export.clicked.connect(self.export_image)

        self.preview_layout.addWidget(QLabel("Result Preview:"))
        self.preview_layout.addWidget(self.lbl_preview, stretch=1)
        self.preview_layout.addWidget(QLabel("Output Bit Depth:"))
        self.preview_layout.addWidget(self.cmb_bit_depth)
        self.preview_layout.addWidget(self.btn_export)

        self.main_layout.addLayout(self.preview_layout, stretch=1)

        # Update Timer (debounce preview)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(100)  # 100ms debounce
        self.update_timer.timeout.connect(self.update_preview)

        # Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Style
        self.setStyleSheet(DARK_THEME)

        # Trigger initial empty preview
        self.request_preview_update()

    def request_preview_update(self):
        self.update_timer.start()

    def handle_smart_load(self, path):
        """
        If a file is dropped on one widget, try to populate others
        if it's an RGB image and they are 'empty' or reset logic is desired.
        Requirement: "If an RGB image is drag/dropped it should load it into the R G and B channel slots"
        """
        # Determine if we should populate others.
        # Sender is the widget that received the drop.
        sender = self.sender()

        # Avoid recursive loops if we call load_image_from_path below
        # But we are calling methods, not dropping.

        # Check if file has > 2 channels (RGB)
        # Ideally we peek at the file or check the widget's loaded data
        if sender and sender.current_image_data is not None:
            img = sender.current_image_data
            if img.ndim == 3 and img.shape[2] >= 3:
                # It's color. Populate R, G, B widgets
                # We only populate if they are not already set to something else?
                # Or force override as per "User wants to repack quickly"? Use force override.

                # Logic: If I drop on R, I update G and B.
                # If I drop on A, maybe don't update RGB?
                # Let's check sender color code.
                if sender.color_code in ["R", "G", "B"]:
                    # Cycle through R, G, B widgets and update them
                    for w in [self.widget_r, self.widget_g, self.widget_b]:
                        if w != sender:  # Don't reload sender
                            # Only populate if the target widget is empty
                            if w.current_image_path is None:
                                w.blockSignals(True)  # Prevent triple preview update
                                w.load_image_from_path(path)
                                w.btn_image_mode.setChecked(True)
                                w.blockSignals(False)
                                w.update_ui_state()  # Ensure UI reflects image mode

                    # Request one update at the end
                    self.request_preview_update()

    def validate_resolutions(self):
        """
        Checks if all active image channels have the same resolution.
        Returns (True, width, height) if consistent or empty.
        Returns (False, details_str, None) if inconsistent.
        """
        shapes = {}

        # Check all widgets
        for w in [self.widget_r, self.widget_g, self.widget_b, self.widget_a]:
            # Only check if in Image Mode and has data
            if w.is_image_mode and w.current_image_data is not None:
                h, width = w.current_image_data.shape[:2]
                res_key = (width, h)
                if res_key not in shapes:
                    shapes[res_key] = []
                shapes[res_key].append(
                    w.title()
                )  # Use widget title (e.g. "Red Output")

        if len(shapes) > 1:
            # Mismatch found
            details = "Resolution Mismatch: "
            parts = []
            for res, widgets in shapes.items():
                parts.append(f"{res[0]}x{res[1]} ({', '.join(widgets)})")
            return False, details + " | ".join(parts), None

        # Consistent
        if len(shapes) == 1:
            w, h = list(shapes.keys())[0]
            return True, "", (w, h)

        return True, "", None  # No images loaded

    def update_preview(self):
        # 1. Validate Resolutions First
        is_valid, error_msg, shape = self.validate_resolutions()

        if not is_valid:
            # Set full error in StatusBar
            self.status_bar.showMessage(error_msg)
            self.status_bar.setStyleSheet(
                "QStatusBar { color: #ff5555; font-weight: bold; }"
            )

            # Show concise error in Preview
            self.lbl_preview.setText("Resolution Error!\nSee details below.")
            self.lbl_preview.setStyleSheet(
                "QLabel { color: #ff5555; font-weight: bold; background-color: #1a1a1a; border: 1px solid #553333; padding: 10px; }"
            )
            return

        # Restore style / Clear error
        self.status_bar.showMessage("Ready")
        self.status_bar.setStyleSheet("")  # Reset
        self.lbl_preview.setStyleSheet(
            "background-color: #1a1a1a; border: 1px solid #333; color: #888;"
        )

        # Gather data
        r = self.widget_r.get_data()
        g = self.widget_g.get_data()
        b = self.widget_b.get_data()
        a = self.widget_a.get_data()

        # If alpha is None and is in Image Mode, create a solid white channel so image is visible in preview
        if shape is not None and a is None and self.widget_a.is_image_mode:
            a = 255

        merged = merge_channels([r, g, b, a])

        if merged is None:
            self.lbl_preview.setText("No Output")
            self.lbl_preview.setPixmap(QPixmap())
            return

        # Convert to QImage for display
        # QImage needs uint8.
        # If merged is 16-bit, downsample.
        if merged.dtype == np.uint16:
            preview_data = normalize_to_8bit(merged)
        else:
            preview_data = merged.astype(np.uint8)

        height, width, channels = preview_data.shape
        bytes_per_line = channels * width

        # Format
        fmt = QImage.Format_RGBA8888

        try:
            q_img = QImage(preview_data.data, width, height, bytes_per_line, fmt)
            # Create pixmap and scale to fit label keeping aspect ratio
            pixmap = QPixmap.fromImage(q_img)
            w, h = self.lbl_preview.width(), self.lbl_preview.height()
            scaled_pix = pixmap.scaled(
                w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.lbl_preview.setPixmap(scaled_pix)
        except Exception as e:
            self.lbl_preview.setText(f"Preview Error: {e}")

    def export_image(self):
        # Validate before export
        is_valid, msg, _ = self.validate_resolutions()
        if not is_valid:
            QMessageBox.critical(self, "Resolution Mismatch", f"Cannot export.\n{msg}")
            return

        r = self.widget_r.get_data()
        g = self.widget_g.get_data()
        b = self.widget_b.get_data()
        a = self.widget_a.get_data()

        # If alpha is None and is in Image Mode, create a solid white channel so image is visible when exported
        # It is unlikely the user would want to export a transparent image and they can set to 'value' mode if they want to export a fully transparent image for any reason
        if a is None and self.widget_a.is_image_mode:
            a = 255

        merged = merge_channels([r, g, b, a])

        # If a merge fails we should be annoying and show an alert as well as the message in the status bar
        if merged is None:
            QMessageBox.warning(self, "No Data", "Nothing to export! Load some images.")
            self.status_bar.showMessage("Nothing to export! Load some images.")
            self.status_bar.setStyleSheet(
                "QStatusBar { color: #ff5555; font-weight: bold; }"
            )
            return

        # Determine target bit depth from combo box selection
        depth_index = self.cmb_bit_depth.currentIndex()
        target_depth = None  # Auto
        if depth_index == 1:
            target_depth = "8bit"
        elif depth_index == 2:
            target_depth = "16bit"
        elif depth_index == 3:
            target_depth = "32bit"

        # Get file filter based on bit depth
        file_filter = get_save_file_filter(target_depth)

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Texture", self.last_directory, file_filter
        )
        if path:
            self.last_directory = str(Path(path).parent)
            success = save_image(path, merged, target_depth)
            if success:
                # Users did not like the abruptness of the alert created by QMessageBox
                # TODO: Can we maybe play a sound too?
                # QMessageBox.information(self, "Success", f"Saved to {path}")
                self.status_bar.showMessage(f"Saved to {path}")
                self.status_bar.setStyleSheet(
                    "QStatusBar { color: #55ff55; font-weight: bold; }"
                )
                self.success_sound.play()
            else:
                # QMessageBox.critical(self, "Error", "Failed to save image.")
                self.status_bar.showMessage("Failed to save image.")
                self.status_bar.setStyleSheet(
                    "QStatusBar { color: #ff5555; font-weight: bold; }"
                )
                self.error_sound.play()
