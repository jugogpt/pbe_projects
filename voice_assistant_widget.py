"""
Voice Assistant GUI Widget with Avatar and Real-time Display
Modern AI assistant interface integrated into the Activity Tracker
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTextEdit, QLabel, QFrame, QScrollArea, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QBrush
import os
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from voice_assistant import VoiceAssistant


class AssistantWorker(QThread):
    """Background worker for voice assistant"""
    transcript_received = pyqtSignal(str)
    response_received = pyqtSignal(str)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.assistant = None

    def run(self):
        """Initialize assistant in background thread"""
        try:
            self.assistant = VoiceAssistant(api_key=self.api_key)

            # Set up callbacks
            self.assistant.on_transcript = self.transcript_received.emit
            self.assistant.on_response = self.response_received.emit
            self.assistant.on_status = self.status_update.emit
            self.assistant.on_error = self.error_occurred.emit

            self.status_update.emit("Assistant initialized")

        except Exception as e:
            self.error_occurred.emit(f"Initialization failed: {str(e)}")

    def start_recording(self):
        """Start voice recording"""
        if self.assistant:
            self.assistant.start_recording()

    def stop_recording(self):
        """Stop voice recording"""
        if self.assistant:
            self.assistant.stop_recording()

    def send_text(self, text):
        """Send text message"""
        if self.assistant:
            self.assistant.send_text_message(text)

    def clear_history(self):
        """Clear conversation history"""
        if self.assistant:
            self.assistant.clear_history()

    def get_transcript_file(self):
        """Get transcript file path"""
        if self.assistant:
            return self.assistant.get_transcript_file_path()
        return None

    def cleanup(self):
        """Cleanup assistant"""
        if self.assistant:
            self.assistant.cleanup()


class VoiceAssistantWidget(QWidget):
    """Modern voice assistant widget with avatar and real-time interaction"""

    def __init__(self, api_key=None, parent=None):
        super().__init__(parent)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.assistant_worker = None
        self.is_recording = False

        self.setup_ui()
        self.apply_styles()
        self.initialize_assistant()

    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Title section
        title_layout = QHBoxLayout()

        title_label = QLabel("🎙️ AI Voice Assistant")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 24px;
                font-weight: 600;
                color: #ffffff;
                padding: 10px 0px;
            }
        """)
        title_layout.addWidget(title_label)

        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            QLabel {
                font-size: 28px;
                color: #666;
                padding: 0px 10px;
            }
        """)
        title_layout.addWidget(self.status_indicator, alignment=Qt.AlignRight)

        main_layout.addLayout(title_layout)

        # Avatar section
        avatar_frame = QFrame()
        avatar_frame.setFixedHeight(200)
        avatar_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(100, 120, 255, 0.15),
                    stop:1 rgba(120, 80, 255, 0.15));
                border: 2px solid rgba(120, 140, 255, 0.3);
                border-radius: 15px;
            }
        """)

        avatar_layout = QVBoxLayout(avatar_frame)

        self.avatar_label = QLabel("🤖")
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                font-size: 80px;
                background: transparent;
            }
        """)
        avatar_layout.addWidget(self.avatar_label)

        self.avatar_status = QLabel("Initializing...")
        self.avatar_status.setAlignment(Qt.AlignCenter)
        self.avatar_status.setStyleSheet("""
            QLabel {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
                color: rgba(200, 210, 255, 0.9);
                background: transparent;
                padding: 5px;
            }
        """)
        avatar_layout.addWidget(self.avatar_status)

        main_layout.addWidget(avatar_frame)

        # Conversation display
        conv_label = QLabel("Conversation")
        conv_label.setStyleSheet("""
            QLabel {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 600;
                color: rgba(160, 170, 200, 0.8);
                padding: 10px 0px 8px 0px;
                border-bottom: 1.5px solid rgba(100, 120, 255, 0.15);
                letter-spacing: 1.5px;
                text-transform: uppercase;
            }
        """)
        main_layout.addWidget(conv_label)

        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setMinimumHeight(300)
        self.conversation_display.setPlaceholderText(
            "💬 Your conversation with the AI assistant will appear here...\n\n"
            "• Click 'Start Listening' to begin voice interaction\n"
            "• Type a message below for text interaction\n"
            "• All conversations are automatically saved"
        )
        main_layout.addWidget(self.conversation_display)

        # Text input section
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type a message or use voice...")
        self.text_input.returnPressed.connect(self.send_text_message)
        input_layout.addWidget(self.text_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(100)
        self.send_btn.clicked.connect(self.send_text_message)
        input_layout.addWidget(self.send_btn)

        main_layout.addLayout(input_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.record_btn = QPushButton("🎤 Start Listening")
        self.record_btn.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_btn)

        self.clear_btn = QPushButton("🗑️ Clear History")
        self.clear_btn.clicked.connect(self.clear_conversation)
        button_layout.addWidget(self.clear_btn)

        self.transcript_btn = QPushButton("📝 Open Transcript")
        self.transcript_btn.clicked.connect(self.open_transcript_file)
        button_layout.addWidget(self.transcript_btn)

        main_layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 11px;
                color: rgba(160, 170, 200, 0.7);
                padding: 8px;
            }
        """)
        main_layout.addWidget(self.status_label)

        # Pulse animation timer
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.update_avatar_pulse)
        self.pulse_state = 0

    def apply_styles(self):
        """Apply modern AI theme styles"""
        # Main widget style
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        # Conversation display style
        self.conversation_display.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 25, 42, 0.92),
                    stop:0.5 rgba(18, 23, 38, 0.95),
                    stop:1 rgba(15, 20, 35, 0.92));
                border: 1.5px solid rgba(120, 140, 255, 0.25);
                border-radius: 12px;
                padding: 20px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
                color: #e2e6f0;
                line-height: 1.6;
            }
        """)

        # Text input style
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: rgba(20, 25, 40, 0.85);
                border: 1px solid rgba(100, 120, 255, 0.2);
                border-radius: 10px;
                padding: 12px 16px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 13px;
                color: #d8dce6;
            }
            QLineEdit:focus {
                border: 1.5px solid rgba(120, 140, 255, 0.5);
                background: rgba(25, 30, 50, 0.9);
            }
        """)

        # Button styles
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(100, 120, 255, 0.85),
                    stop:0.5 rgba(80, 100, 240, 0.9),
                    stop:1 rgba(90, 110, 250, 0.85));
                border: 1px solid rgba(120, 140, 255, 0.4);
                border-radius: 10px;
                padding: 12px 20px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 500;
                color: #ffffff;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(120, 140, 255, 0.95),
                    stop:0.5 rgba(100, 120, 255, 1.0),
                    stop:1 rgba(110, 130, 255, 0.95));
                border: 1px solid rgba(140, 160, 255, 0.6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(70, 90, 220, 0.95),
                    stop:1 rgba(80, 100, 230, 0.95));
            }
            QPushButton:disabled {
                background: rgba(40, 45, 60, 0.5);
                border: 1px solid rgba(60, 70, 90, 0.3);
                color: rgba(200, 205, 215, 0.4);
            }
        """

        self.record_btn.setStyleSheet(button_style)
        self.send_btn.setStyleSheet(button_style)
        self.clear_btn.setStyleSheet(button_style)
        self.transcript_btn.setStyleSheet(button_style)

    def initialize_assistant(self):
        """Initialize the voice assistant in background"""
        if not self.api_key:
            self.add_system_message("❌ OpenAI API key not configured")
            self.record_btn.setEnabled(False)
            self.send_btn.setEnabled(False)
            return

        self.assistant_worker = AssistantWorker(self.api_key)
        self.assistant_worker.transcript_received.connect(self.on_transcript)
        self.assistant_worker.response_received.connect(self.on_response)
        self.assistant_worker.status_update.connect(self.on_status_update)
        self.assistant_worker.error_occurred.connect(self.on_error)
        self.assistant_worker.start()

    def toggle_recording(self):
        """Toggle voice recording"""
        if not self.assistant_worker:
            return

        if not self.is_recording:
            # Start recording
            self.assistant_worker.start_recording()
            self.is_recording = True
            self.record_btn.setText("⏹️ Stop Listening")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 80, 80, 0.85),
                        stop:1 rgba(255, 100, 100, 0.85));
                    border: 1px solid rgba(255, 120, 120, 0.4);
                    border-radius: 10px;
                    padding: 12px 20px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 500;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 100, 100, 0.95),
                        stop:1 rgba(255, 120, 120, 0.95));
                }
            """)
            self.status_indicator.setStyleSheet("QLabel { font-size: 28px; color: #ff4444; }")
            self.pulse_timer.start(500)  # Pulse animation
            self.avatar_status.setText("Listening...")
        else:
            # Stop recording
            self.assistant_worker.stop_recording()
            self.is_recording = False
            self.record_btn.setText("🎤 Start Listening")
            self.apply_styles()  # Reset button style
            self.status_indicator.setStyleSheet("QLabel { font-size: 28px; color: #4444ff; }")
            self.pulse_timer.stop()
            self.avatar_status.setText("Ready")

    def send_text_message(self):
        """Send text message to assistant"""
        text = self.text_input.text().strip()
        if not text or not self.assistant_worker:
            return

        self.text_input.clear()
        self.assistant_worker.send_text(text)

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_display.clear()
        if self.assistant_worker:
            self.assistant_worker.clear_history()
        self.add_system_message("✓ Conversation cleared")

    def open_transcript_file(self):
        """Open the transcript file in explorer"""
        if self.assistant_worker:
            transcript_file = self.assistant_worker.get_transcript_file()
            if transcript_file and os.path.exists(transcript_file):
                os.startfile(os.path.dirname(transcript_file))
                self.add_system_message(f"📂 Opened: {os.path.basename(transcript_file)}")

    def on_transcript(self, text):
        """Handle transcribed user speech"""
        self.add_message("You", text, "#8c9eff")

    def on_response(self, text):
        """Handle AI response"""
        self.add_message("AI Assistant", text, "#4caf50")

    def on_status_update(self, status):
        """Handle status updates"""
        self.status_label.setText(status)

    def on_error(self, error):
        """Handle errors"""
        self.add_system_message(f"❌ {error}")

    def add_message(self, sender, content, color="#ffffff"):
        """Add a message to the conversation display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f'<div style="margin: 10px 0px;">'
        formatted_message += f'<span style="color: {color}; font-weight: 600;">[{timestamp}] {sender}:</span><br>'
        formatted_message += f'<span style="color: #d8dce6; margin-left: 10px;">{content}</span>'
        formatted_message += '</div>'

        self.conversation_display.append(formatted_message)
        self.conversation_display.verticalScrollBar().setValue(
            self.conversation_display.verticalScrollBar().maximum()
        )

    def add_system_message(self, message):
        """Add a system message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f'<div style="margin: 8px 0px; color: rgba(160, 170, 200, 0.8);">'
        formatted_message += f'[{timestamp}] {message}'
        formatted_message += '</div>'

        self.conversation_display.append(formatted_message)

    def update_avatar_pulse(self):
        """Update avatar pulse animation"""
        self.pulse_state = (self.pulse_state + 1) % 2
        if self.pulse_state == 0:
            self.avatar_label.setText("🎙️")
        else:
            self.avatar_label.setText("🔴")

    def closeEvent(self, event):
        """Handle widget close"""
        if self.assistant_worker:
            self.assistant_worker.cleanup()
            self.assistant_worker.quit()
            self.assistant_worker.wait()
        event.accept()
