"""
Beautiful UI styles for Activity Tracker with white/light pink aesthetic and animations
"""

def get_main_stylesheet():
    """Main window stylesheet with clean white/very light pink theme"""
    return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 255),
                stop:0.3 rgba(255, 252, 253, 255),
                stop:0.7 rgba(254, 249, 251, 255),
                stop:1 rgba(255, 255, 255, 255));
            border: none;
        }

        QWidget {
            background: transparent;
            color: #2c2c2c;
        }
    """

def get_text_area_stylesheet():
    """Styled text area with soft pink border and subtle glow"""
    return """
        QTextEdit {
            background: rgba(255, 255, 255, 1.0);
            border: 2px solid rgba(251, 207, 232, 0.5);
            border-radius: 15px;
            padding: 15px;
            font-family: 'Alan Sans';
            font-size: 13px;
            font-weight: 400;
            color: #2c2c2c;
            selection-background-color: rgba(251, 207, 232, 0.3);
            /* Subtle pink glow */
            box-shadow: 0 0 8px rgba(251, 207, 232, 0.2),
                        0 0 15px rgba(251, 207, 232, 0.1);
        }

        QTextEdit:focus {
            border: 2px solid rgba(251, 207, 232, 0.8);
            background: rgba(255, 255, 255, 1.0);
            /* Enhanced glow on focus */
            box-shadow: 0 0 10px rgba(251, 207, 232, 0.3),
                        0 0 20px rgba(251, 207, 232, 0.2);
        }
    """

def get_button_stylesheet():
    """Beautiful animated buttons with pink glow effects"""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 255, 255, 1.0),
                stop:0.5 rgba(254, 248, 250, 1.0),
                stop:1 rgba(253, 242, 246, 1.0));
            border: 2px solid rgba(251, 207, 232, 0.6);
            border-radius: 20px;
            padding: 12px 20px;
            font-family: 'Alan Sans';
            font-size: 14px;
            font-weight: 600;
            color: #2c2c2c;
            min-height: 20px;
            /* Pink glow effect */
            box-shadow: 0 0 10px rgba(251, 207, 232, 0.4),
                        0 0 20px rgba(251, 207, 232, 0.2),
                        0 0 30px rgba(251, 207, 232, 0.1);
        }

        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(253, 242, 246, 1.0),
                stop:0.5 rgba(251, 207, 232, 0.8),
                stop:1 rgba(248, 187, 208, 0.6));
            border: 2px solid rgba(245, 167, 184, 0.8);
            /* Enhanced pink glow on hover */
            box-shadow: 0 0 15px rgba(251, 207, 232, 0.6),
                        0 0 25px rgba(251, 207, 232, 0.4),
                        0 0 35px rgba(251, 207, 232, 0.2),
                        0 0 45px rgba(245, 167, 184, 0.1);
            transform: translateY(-1px);
        }

        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(248, 187, 208, 0.8),
                stop:1 rgba(251, 207, 232, 0.9));
            border: 2px solid rgba(245, 167, 184, 1.0);
            /* Soft glow when pressed */
            box-shadow: 0 0 8px rgba(251, 207, 232, 0.5),
                        0 0 15px rgba(251, 207, 232, 0.3);
            transform: translateY(1px);
        }

        QPushButton:focus {
            border: 2px solid rgba(245, 167, 184, 1.0);
            /* Focus glow */
            box-shadow: 0 0 12px rgba(251, 207, 232, 0.5),
                        0 0 20px rgba(251, 207, 232, 0.3),
                        0 0 30px rgba(251, 207, 232, 0.2);
        }
    """

def get_hotkey_label_stylesheet():
    """Elegant hotkey indicator with beautiful pink glow"""
    return """
        QLabel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 1.0),
                stop:0.5 rgba(254, 248, 250, 1.0),
                stop:1 rgba(255, 255, 255, 1.0));
            border: 2px solid rgba(251, 207, 232, 0.5);
            border-radius: 12px;
            padding: 8px 16px;
            font-family: 'Mochiy Pop One';
            font-size: 12px;
            font-weight: normal;
            color: #d63384;
            margin: 5px;
            /* Beautiful pink glow */
            box-shadow: 0 0 12px rgba(251, 207, 232, 0.4),
                        0 0 20px rgba(251, 207, 232, 0.2),
                        0 0 30px rgba(251, 207, 232, 0.1);
        }
    """

def get_title_label_stylesheet():
    """Beautiful title styling"""
    return """
        QLabel {
            font-family: 'Mochiy Pop One';
            font-size: 24px;
            font-weight: normal;
            color: #d63384;
            background: transparent;
            margin: 10px 0px;
        }
    """

def get_section_label_stylesheet():
    """Section headers with elegant styling"""
    return """
        QLabel {
            font-family: 'Alan Sans';
            font-size: 16px;
            font-weight: 700;
            color: #6c757d;
            background: transparent;
            margin: 8px 0px 4px 0px;
        }
    """

def get_scroll_area_stylesheet():
    """Custom scrollbar with pink theme"""
    return """
        QScrollBar:vertical {
            background: rgba(251, 207, 232, 0.2);
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }

        QScrollBar::handle:vertical {
            background: rgba(251, 207, 232, 0.6);
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background: rgba(245, 167, 184, 0.8);
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: none;
        }
    """