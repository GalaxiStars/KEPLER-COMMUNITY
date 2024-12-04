from PySide6.QtCore import Qt, QPoint, QOperatingSystemVersion
from PySide6.QtGui import QIcon, QColor, QPainterPath, QPainter
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QWidget, QSpinBox
)
from styles import (
    get_resource_dialog_style, get_custom_input_dialog_style,
    get_dialog_title_style, get_dialog_title_label_style,
    get_dialog_close_button_style
)

class DraggableTitle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._mousePressed = False
        self._mousePos = QPoint()
        self._windowPos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressed = True
            self._mousePos = event.globalPosition().toPoint()
            self._windowPos = self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._mousePressed:
            delta = event.globalPosition().toPoint() - self._mousePos
            self.window().move(self._windowPos + delta)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressed = False
            event.accept()

class CustomInputDialog(QDialog):
    def __init__(self, parent=None, title="", label="", text=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_windows_10 = QOperatingSystemVersion.current() == QOperatingSystemVersion.Windows10
        
        if self.is_windows_10:
            self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        self.setStyleSheet(get_custom_input_dialog_style(self.is_windows_10))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 10)

        # Custom title bar
        self.title_bar = DraggableTitle(self)
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet(get_dialog_title_style())
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet(get_dialog_title_label_style())
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_button = QPushButton()
        close_button.setIcon(QIcon('Images/close-64.png'))
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(get_dialog_close_button_style())
        close_button.clicked.connect(self.reject)
        title_layout.addWidget(close_button)

        main_layout.addWidget(self.title_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 10, 20, 10)

        self.label = QLabel(label)
        content_layout.addWidget(self.label)

        self.input = QLineEdit(text)
        content_layout.addWidget(self.input)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        content_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)

    def paintEvent(self, event):
        if not self.is_windows_10:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            path = QPainterPath()
            path.addRoundedRect(self.rect(), 10, 10)
            
            painter.setClipPath(path)
            painter.fillPath(path, QColor("#240970"))
        else:
            super().paintEvent(event)

    def get_input(self):
        return self.input.text()

class ResourceDialog(QDialog):
    def __init__(self, parent=None, current_values=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_windows_10 = QOperatingSystemVersion.current() == QOperatingSystemVersion.Windows10
        
        if self.is_windows_10:
            self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        self.setStyleSheet(get_resource_dialog_style(self.is_windows_10))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 10)

        # Custom title bar
        self.title_bar = DraggableTitle(self)
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet(get_dialog_title_style())
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Resource Management")
        title_label.setStyleSheet(get_dialog_title_label_style())
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_button = QPushButton()
        close_button.setIcon(QIcon('Images/close-64.png'))
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(get_dialog_close_button_style())
        close_button.clicked.connect(self.reject)
        title_layout.addWidget(close_button)

        main_layout.addWidget(self.title_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 10, 20, 10)
        content_layout.setSpacing(15)

        # CPU Limit
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU Limit (%):")
        self.cpu_spinbox = QSpinBox()
        self.cpu_spinbox.setRange(0, 100)
        self.cpu_spinbox.setValue(current_values['cpu'] if current_values else 100)
        self.cpu_spinbox.setFixedWidth(150)
        self.cpu_spinbox.setAlignment(Qt.AlignCenter)
        self.cpu_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(25, 25)
        plus_btn.setAutoRepeat(True)
        plus_btn.setAutoRepeatDelay(300)
        plus_btn.setAutoRepeatInterval(100)
        plus_btn.clicked.connect(lambda: self.cpu_spinbox.setValue(self.cpu_spinbox.value() + 1))
        
        minus_btn = QPushButton("-")
        minus_btn.setFixedSize(25, 25)
        minus_btn.setAutoRepeat(True)
        minus_btn.setAutoRepeatDelay(300)
        minus_btn.setAutoRepeatInterval(100)
        minus_btn.clicked.connect(lambda: self.cpu_spinbox.setValue(self.cpu_spinbox.value() - 1))
        
        spinbox_layout = QHBoxLayout()
        spinbox_layout.setSpacing(5)
        spinbox_layout.addWidget(plus_btn)
        spinbox_layout.addWidget(self.cpu_spinbox)
        spinbox_layout.addWidget(minus_btn)
        
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addLayout(spinbox_layout)
        cpu_layout.addStretch()
        content_layout.addLayout(cpu_layout)

        # Memory Limit
        memory_layout = QHBoxLayout()
        memory_label = QLabel("Memory Limit (MB):")
        self.memory_spinbox = QSpinBox()
        self.memory_spinbox.setRange(0, 32768)
        self.memory_spinbox.setValue(current_values['memory'] if current_values else 0)
        self.memory_spinbox.setFixedWidth(150)
        self.memory_spinbox.setAlignment(Qt.AlignCenter)
        self.memory_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        
        plus_btn_mem = QPushButton("+")
        plus_btn_mem.setFixedSize(25, 25)
        plus_btn_mem.setAutoRepeat(True)
        plus_btn_mem.setAutoRepeatDelay(300)
        plus_btn_mem.setAutoRepeatInterval(100)
        plus_btn_mem.clicked.connect(lambda: self.memory_spinbox.setValue(self.memory_spinbox.value() + 100))
        
        minus_btn_mem = QPushButton("-")
        minus_btn_mem.setFixedSize(25, 25)
        minus_btn_mem.setAutoRepeat(True)
        minus_btn_mem.setAutoRepeatDelay(300)
        minus_btn_mem.setAutoRepeatInterval(100)
        minus_btn_mem.clicked.connect(lambda: self.memory_spinbox.setValue(self.memory_spinbox.value() - 100))
        
        spinbox_layout_mem = QHBoxLayout()
        spinbox_layout_mem.setSpacing(5)
        spinbox_layout_mem.addWidget(plus_btn_mem)
        spinbox_layout_mem.addWidget(self.memory_spinbox)
        spinbox_layout_mem.addWidget(minus_btn_mem)
        
        memory_layout.addWidget(memory_label)
        memory_layout.addLayout(spinbox_layout_mem)
        memory_layout.addStretch()
        content_layout.addLayout(memory_layout)

        # Network Limit
        network_layout = QHBoxLayout()
        network_label = QLabel("Network Limit (kbps):")
        self.network_spinbox = QSpinBox()
        self.network_spinbox.setRange(0, 1000000)
        self.network_spinbox.setValue(current_values['network'] if current_values else 0)
        self.network_spinbox.setFixedWidth(150)
        self.network_spinbox.setAlignment(Qt.AlignCenter)
        self.network_spinbox.setButtonSymbols(QSpinBox.NoButtons)
        
        plus_btn_net = QPushButton("+")
        plus_btn_net.setFixedSize(25, 25)
        plus_btn_net.setAutoRepeat(True)
        plus_btn_net.setAutoRepeatDelay(300)
        plus_btn_net.setAutoRepeatInterval(100)
        plus_btn_net.clicked.connect(lambda: self.network_spinbox.setValue(self.network_spinbox.value() + 1000))
        
        minus_btn_net = QPushButton("-")
        minus_btn_net.setFixedSize(25, 25)
        minus_btn_net.setAutoRepeat(True)
        minus_btn_net.setAutoRepeatDelay(300)
        minus_btn_net.setAutoRepeatInterval(100)
        minus_btn_net.clicked.connect(lambda: self.network_spinbox.setValue(self.network_spinbox.value() - 1000))
        
        spinbox_layout_net = QHBoxLayout()
        spinbox_layout_net.setSpacing(5)
        spinbox_layout_net.addWidget(plus_btn_net)
        spinbox_layout_net.addWidget(self.network_spinbox)
        spinbox_layout_net.addWidget(minus_btn_net)
        
        network_layout.addWidget(network_label)
        network_layout.addLayout(spinbox_layout_net)
        network_layout.addStretch()
        content_layout.addLayout(network_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.accept)
        button_layout.addWidget(apply_button)

        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        content_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)

        # Set fixed size for the dialog
        self.setFixedSize(400, 300)

    def paintEvent(self, event):
        if not self.is_windows_10:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            path = QPainterPath()
            path.addRoundedRect(self.rect(), 10, 10)
            
            painter.setClipPath(path)
            painter.fillPath(path, QColor("#240970"))
        else:
            super().paintEvent(event)

    def reset_to_default(self):
        self.cpu_spinbox.setValue(100)
        self.memory_spinbox.setValue(0)
        self.network_spinbox.setValue(0)