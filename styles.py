def get_main_window_style():
    return """
        QMainWindow {
            background-color: #240970;
            border: none;
        }
        QWidget#titleBar {
            background-color: #1a0748;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
    """

def get_toolbar_style():
    return """
        QToolBar {
            background-color: #240970;
            spacing: 10px;
            border: none;
        }
    """

def get_button_style():
    return """
        QPushButton {
            background-color: transparent;
            border-style: none;
            border-width: 0px;
            border-radius: 10px;
            border-color: transparent;
            font: bold 16px;
            min-width: 1em;
            padding: 4px;
        }
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1a0748, stop:1 #1d1580);
            color: white;
            font-weight: bold;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #261FA0, stop:1 #200860);
        }
    """

def get_line_edit_style(light_mode=False):
    if light_mode:
        return """
            QLineEdit {
                border-radius: 10px;
                padding: 0 8px;
                selection-background-color: lightgray;
                font-size: 20px;
            }
            QLineEdit:focus {
                border: 2px solid black;
            }
        """
    else:
        return """
            QLineEdit {
                border-radius: 10px;
                padding: 0 8px;
                selection-background-color: darkgray;
                font-size: 20px;
            }
            QLineEdit:focus {
                border: 2px solid lightgray;
            }
        """

def get_title_button_style():
    return """
        QPushButton {
            background-color: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 30);
        }
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 50);
        }
    """

def get_bookmark_menu_style():
    return """
        QWidget {
            background-color: #240970;
            border: 2px solid #1a0748;
            border-radius: 10px;
        }
        QPushButton {
            color: white;
            background-color: transparent;
            border: none;
            text-align: left;
            padding: 8px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #1a0748;
        }
        QLabel {
            color: white;
            padding: 8px;
            font-weight: bold;
        }
    """

def get_bookmark_header_style():
    return """
        font-size: 14px;
        border-bottom: 1px solid #1a0748;
    """

def get_resource_dialog_style(is_windows_10=False):
    base_style = """
        QDialog {
            background-color: #240970;
            color: white;
            border: 1px solid #3d1db8;
            %s
        }
        QLabel {
            color: white;
            font-size: 14px;
        }
        QSpinBox {
            background-color: #1a0748;
            color: white;
            border: 1px solid #3d1db8;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
            min-width: 150px;
        }
        QSpinBox::up-button {
            width: 25px;
            border-left: 1px solid #3d1db8;
            border-bottom: 1px solid #3d1db8;
            border-top-right-radius: 5px;
            background: #1a0748;
            subcontrol-origin: border;
            subcontrol-position: top right;
        }
        QSpinBox::up-button:hover {
            background: #4f29d6;
        }
        QSpinBox::up-arrow {
            width: 12px;
            height: 12px;
            color: white;
            font-size: 14px;
        }
        QSpinBox::down-button {
            width: 25px;
            border-left: 1px solid #3d1db8;
            border-top: 1px solid #3d1db8;
            border-bottom-right-radius: 5px;
            background: #1a0748;
            subcontrol-origin: border;
            subcontrol-position: bottom right;
        }
        QSpinBox::down-button:hover {
            background: #4f29d6;
        }
        QSpinBox::down-arrow {
            width: 12px;
            height: 12px;
            color: white;
            font-size: 14px;
        }
        QPushButton {
            background-color: #3d1db8;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #4f29d6;
        }
    """ % ("" if is_windows_10 else "border-radius: 10px;")
    
    return base_style

def get_custom_input_dialog_style(is_windows_10=False):
    if is_windows_10:
        return """
            QDialog {
                background-color: #240970;
                color: white;
                border: 1px solid #3d1db8;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1a0748;
                color: white;
                border: 1px solid #3d1db8;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3d1db8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4f29d6;
            }
        """
    else:
        return """
            QDialog {
                background-color: #240970;
                color: white;
                border: 1px solid #3d1db8;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1a0748;
                color: white;
                border: 1px solid #3d1db8;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3d1db8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4f29d6;
            }
        """

def get_dialog_title_style():
    return """
        background-color: #240970; 
        border-top-left-radius: 10px; 
        border-top-right-radius: 10px;
    """

def get_dialog_title_label_style():
    return """
        font-weight: bold; 
        font-size: 16px;
    """

def get_dialog_close_button_style():
    return """
        background-color: transparent;
    """