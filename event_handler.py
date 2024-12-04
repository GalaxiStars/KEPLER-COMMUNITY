from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtWidgets import QWidget

class DraggableTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.pressing = False
        self.start_point = QPoint(0, 0)
        self.parent = parent
        QTimer.singleShot(0, self.setup_timer)

    def setup_timer(self):
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.perform_resize)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressing = True
            self.start_point = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.pressing:
            move_vector = event.globalPosition().toPoint() - self.start_point
            self.parent.move(self.parent.pos() + move_vector)
            self.start_point = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressing = False
            # Check if the window is near the top of the screen
            if self.parent.pos().y() < 10:
                self.parent.showMaximized()
            else:
                # Only start timer if it exists
                if hasattr(self, 'resize_timer'):
                    self.resize_timer.start(100)  # Delay resize for better performance
            event.accept()

    def perform_resize(self):
        current_size = self.parent.size()
        if current_size.width() < 1200 or current_size.height() < 800:
            self.parent.resize(1200, 800)

    def mouseDoubleClickEvent(self, event):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
        event.accept()