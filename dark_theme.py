"""
Modern AI application theme with sophisticated gradients and professional styling
"""

def get_main_dark_stylesheet():
    """Main window with premium dark gradient theme inspired by modern AI apps"""
    return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0e1a,
                stop:0.3 #121829,
                stop:0.7 #1a1f35,
                stop:1 #0f1419);
            border: none;
        }

        QWidget {
            background: transparent;
            color: #e4e8f0;
            font-family: 'Segoe UI', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        QSplitter::handle {
            background: rgba(100, 120, 255, 0.15);
            border-radius: 2px;
        }

        QSplitter::handle:hover {
            background: rgba(100, 120, 255, 0.3);
        }
    """

def get_dark_text_area_stylesheet():
    """Premium text area with glass morphism and professional typography"""
    return """
        QTextEdit, QListWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(20, 25, 40, 0.85),
                stop:1 rgba(15, 20, 35, 0.95));
            border: 1px solid rgba(100, 120, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Text', -apple-system, sans-serif;
            font-size: 14px;
            font-weight: 400;
            color: #d8dce6;
            selection-background-color: rgba(120, 140, 255, 0.25);
            line-height: 1.65;
        }

        QTextEdit:focus, QListWidget:focus {
            border: 1.5px solid rgba(120, 140, 255, 0.5);
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(25, 30, 50, 0.9),
                stop:1 rgba(20, 25, 45, 0.98));
            box-shadow: 0 0 25px rgba(100, 120, 255, 0.15);
        }

        QListWidget::item {
            padding: 14px 16px;
            border-radius: 8px;
            margin: 3px 0;
            font-size: 13.5px;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }

        QListWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(100, 120, 255, 0.25),
                stop:0.5 rgba(120, 80, 255, 0.2),
                stop:1 rgba(100, 120, 255, 0.25));
            border: 1px solid rgba(120, 140, 255, 0.4);
            color: #ffffff;
        }

        QListWidget::item:hover {
            background: rgba(80, 90, 130, 0.3);
            border: 1px solid rgba(100, 120, 255, 0.2);
        }

        /* Modern scrollbar */
        QScrollBar:vertical {
            background: rgba(20, 25, 40, 0.4);
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }

        QScrollBar::handle:vertical {
            background: rgba(100, 120, 255, 0.3);
            border-radius: 5px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background: rgba(120, 140, 255, 0.5);
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
    """

def get_dark_button_stylesheet():
    """Premium buttons with modern AI app styling and smooth interactions"""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(100, 120, 255, 0.85),
                stop:0.5 rgba(80, 100, 240, 0.9),
                stop:1 rgba(90, 110, 250, 0.85));
            border: 1px solid rgba(120, 140, 255, 0.4);
            border-radius: 10px;
            padding: 12px 24px;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Display', sans-serif;
            font-size: 13px;
            font-weight: 500;
            color: #ffffff;
            min-height: 22px;
            text-align: center;
            letter-spacing: 0.3px;
        }

        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(120, 140, 255, 0.95),
                stop:0.5 rgba(100, 120, 255, 1.0),
                stop:1 rgba(110, 130, 255, 0.95));
            border: 1px solid rgba(140, 160, 255, 0.6);
            box-shadow: 0 0 20px rgba(100, 120, 255, 0.4),
                        0 4px 15px rgba(80, 100, 240, 0.3);
        }

        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(70, 90, 220, 0.95),
                stop:1 rgba(80, 100, 230, 0.95));
            border: 1px solid rgba(100, 120, 255, 0.8);
            padding-top: 13px;
            padding-bottom: 11px;
        }

        QPushButton:disabled {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(40, 45, 60, 0.5),
                stop:1 rgba(35, 40, 55, 0.5));
            border: 1px solid rgba(60, 70, 90, 0.3);
            color: rgba(200, 205, 215, 0.4);
        }

        QPushButton:focus {
            border: 1.5px solid rgba(140, 160, 255, 0.8);
            outline: none;
            box-shadow: 0 0 15px rgba(120, 140, 255, 0.3);
        }
    """

def get_dark_title_stylesheet():
    """Premium title with sophisticated gradient and modern typography"""
    return """
        QLabel {
            font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
            font-size: 32px;
            font-weight: 600;
            color: #ffffff;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(140, 160, 255, 1.0),
                stop:0.5 rgba(180, 140, 255, 1.0),
                stop:1 rgba(140, 160, 255, 1.0));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 20px 0px 30px 0px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
    """

def get_dark_section_stylesheet():
    """Premium section headers with modern styling"""
    return """
        QLabel {
            font-family: 'Inter', 'Segoe UI', 'SF Pro Text', sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: rgba(160, 170, 200, 0.8);
            background: transparent;
            margin: 20px 0px 12px 0px;
            padding: 10px 0px 8px 0px;
            border-bottom: 1.5px solid rgba(100, 120, 255, 0.15);
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
    """

def get_dark_analysis_text_stylesheet():
    """Premium analysis area with exceptional readability and modern design"""
    return """
        QTextEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(20, 25, 42, 0.92),
                stop:0.5 rgba(18, 23, 38, 0.95),
                stop:1 rgba(15, 20, 35, 0.92));
            border: 1.5px solid rgba(120, 140, 255, 0.25);
            border-radius: 14px;
            padding: 30px;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Text', -apple-system, sans-serif;
            font-size: 15px;
            font-weight: 400;
            color: #e2e6f0;
            selection-background-color: rgba(120, 140, 255, 0.3);
            line-height: 1.75;
        }

        QTextEdit:focus {
            border: 2px solid rgba(140, 160, 255, 0.5);
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(25, 30, 50, 0.95),
                stop:0.5 rgba(22, 27, 45, 0.98),
                stop:1 rgba(20, 25, 40, 0.95));
            box-shadow: 0 0 30px rgba(120, 140, 255, 0.2),
                        0 8px 25px rgba(100, 120, 255, 0.15);
        }
    """

def get_dark_frame_stylesheet():
    """Frames and containers styling"""
    return """
        QFrame {
            background: transparent;
            border: none;
            margin: 4px 0px;
        }
    """