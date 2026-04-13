from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._full_text = text
        self.setText(text)  # initial display

    def setFullText(self, text):
        self._full_text = text
        self._updateElided()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._updateElided()

    def _updateElided(self):
        fm = self.fontMetrics()
        elided = fm.elidedText(
            self._full_text, Qt.TextElideMode.ElideMiddle, self.width()
        )
        super().setText(elided)
