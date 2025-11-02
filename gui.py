import sys
import os
import threading
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QTextEdit, QLabel, QFrame, QSplitter,
                             QGridLayout, QListWidget, QListWidgetItem, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFontDatabase, QFont

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from recorder import record_screen
from tracker import start_tracking
from screenshot import start_hotkey_listener
from utils import ensure_folders, timestamped_filename, init_db
from dark_theme import (get_main_dark_stylesheet, get_dark_text_area_stylesheet,
                        get_dark_button_stylesheet, get_dark_title_stylesheet,
                        get_dark_section_stylesheet, get_dark_analysis_text_stylesheet,
                        get_dark_frame_stylesheet)
from claude_api import video_analyzer
from voice_assistant_widget import VoiceAssistantWidget
from threading import Event
from datetime import datetime


class AnalysisThread(QThread):
    """Thread for running video analysis without blocking UI"""
    analysis_complete = pyqtSignal(str)

    def __init__(self, video_path=None):
        super().__init__()
        self.video_path = video_path

    def run(self):
        if self.video_path:
            analysis = video_analyzer.analyze_video_by_path(self.video_path, detailed=False)
        else:
            analysis = video_analyzer.analyze_latest_recording()
        self.analysis_complete.emit(analysis)


class WorkflowAnalysisThread(QThread):
    """Thread for running detailed workflow analysis without blocking UI"""
    analysis_complete = pyqtSignal(str, str)  # (analysis_text, video_path)

    def __init__(self, video_path=None):
        super().__init__()
        self.video_path = video_path

    def run(self):
        if self.video_path:
            analysis = video_analyzer.analyze_video_by_path(self.video_path, detailed=True)
            self.analysis_complete.emit(analysis, self.video_path)
        else:
            latest = video_analyzer.get_latest_recording()
            analysis = video_analyzer.analyze_latest_workflow()
            self.analysis_complete.emit(analysis, latest if latest else "")


class MainWindow(QMainWindow):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.record_thread = None
        self.stop_event = None
        self.analysis_thread = None
        self.workflow_analysis_thread = None

        self.load_custom_fonts()
        self.setup_dark_ui()
        self.apply_dark_styles()
        self.connect_signals()
        self.start_background_services()

    def load_custom_fonts(self):
        """Load custom fonts from the fonts folder"""
        # Load Alan Sans
        alan_sans_path = "fonts/Alan_Sans/static/AlanSans-Regular.ttf"
        if os.path.exists(alan_sans_path):
            QFontDatabase.addApplicationFont(alan_sans_path)

        # Load Alan Sans Bold
        alan_sans_bold_path = "fonts/Alan_Sans/static/AlanSans-Bold.ttf"
        if os.path.exists(alan_sans_bold_path):
            QFontDatabase.addApplicationFont(alan_sans_bold_path)

        # Load Mochiy Pop One
        mochiy_path = "fonts/Mochiy_Pop_One/MochiyPopOne-Regular.ttf"
        if os.path.exists(mochiy_path):
            QFontDatabase.addApplicationFont(mochiy_path)

    def setup_dark_ui(self):
        """Setup the premium modern AI application UI"""
        self.setWindowTitle("Activity Tracker AI")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        ensure_folders()

        # Main container with modern spacing
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(28)
        main_layout.setContentsMargins(40, 35, 40, 40)

        # Modern title with AI branding
        self.title_label = QLabel("Activity Tracker AI")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Main content splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # Left panel for controls with modern spacing
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(24)
        left_layout.setContentsMargins(0, 0, 10, 0)

        # Activity log section with modern label
        log_label = QLabel("System Activity")
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setMaximumHeight(180)

        # Controls grid with improved spacing
        controls_frame = QFrame()
        controls_layout = QGridLayout(controls_frame)
        controls_layout.setSpacing(14)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Recording controls with modern labels
        recording_label = QLabel("Recording")
        self.start_btn = QPushButton("⏺ Start Recording")
        self.stop_btn = QPushButton("⏹ Stop Recording")

        # Screenshot controls
        screenshot_label = QLabel("Capture")
        self.screenshot_btn = QPushButton("📸 Take Screenshot")

        # File management
        files_label = QLabel("File Management")
        self.folder_btn = QPushButton("📁 Recordings")
        self.screenshots_folder_btn = QPushButton("🖼 Screenshots")
        self.analyses_folder_btn = QPushButton("📊 Analyses")

        # Recording selection
        recordings_label = QLabel("Recording Library")
        self.recordings_list = QListWidget()
        self.recordings_list.setMaximumHeight(160)
        self.refresh_recordings_btn = QPushButton("🔄 Refresh")

        # Analytics with modern labels
        analytics_label = QLabel("AI Analysis")
        self.chart_btn = QPushButton("📈 Usage Chart")
        self.analyze_btn = QPushButton("🤖 Quick Analysis")
        self.workflow_btn = QPushButton("✨ Detailed Workflow")

        # Add to grid layout
        controls_layout.addWidget(recording_label, 0, 0, 1, 2)
        controls_layout.addWidget(self.start_btn, 1, 0)
        controls_layout.addWidget(self.stop_btn, 1, 1)

        controls_layout.addWidget(screenshot_label, 2, 0, 1, 2)
        controls_layout.addWidget(self.screenshot_btn, 3, 0, 1, 2)

        controls_layout.addWidget(files_label, 4, 0, 1, 2)
        controls_layout.addWidget(self.folder_btn, 5, 0)
        controls_layout.addWidget(self.screenshots_folder_btn, 5, 1)
        controls_layout.addWidget(self.analyses_folder_btn, 6, 0, 1, 2)

        controls_layout.addWidget(recordings_label, 7, 0, 1, 2)
        controls_layout.addWidget(self.recordings_list, 8, 0, 1, 2)
        controls_layout.addWidget(self.refresh_recordings_btn, 9, 0, 1, 2)

        controls_layout.addWidget(analytics_label, 10, 0, 1, 2)
        controls_layout.addWidget(self.chart_btn, 11, 0)
        controls_layout.addWidget(self.analyze_btn, 11, 1)
        controls_layout.addWidget(self.workflow_btn, 12, 0, 1, 2)

        # Add to left panel
        left_layout.addWidget(log_label)
        left_layout.addWidget(self.text)
        left_layout.addWidget(controls_frame)
        left_layout.addStretch()

        # Right panel with tabs for analysis and voice assistant
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Create tab widget for right panel
        self.right_tabs = QTabWidget()
        self.right_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(100, 120, 255, 0.2);
                border-radius: 8px;
                background: transparent;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 35, 50, 0.8),
                    stop:1 rgba(25, 30, 45, 0.8));
                border: 1px solid rgba(100, 120, 255, 0.2);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 4px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 500;
                color: rgba(200, 210, 255, 0.7);
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 120, 255, 0.3),
                    stop:1 rgba(80, 100, 240, 0.3));
                color: #ffffff;
                border-color: rgba(120, 140, 255, 0.5);
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(50, 60, 90, 0.8),
                    stop:1 rgba(40, 50, 80, 0.8));
            }
        """)

        # Video Analysis Tab
        analysis_tab = QWidget()
        analysis_tab_layout = QVBoxLayout(analysis_tab)
        analysis_tab_layout.setSpacing(20)
        analysis_tab_layout.setContentsMargins(15, 20, 15, 15)

        analysis_label = QLabel("AI Video Analysis")
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMinimumHeight(350)
        self.analysis_text.setPlaceholderText("🎯 Welcome to Activity Tracker AI\n\n✨ Quick Start Guide:\n\n1️⃣ Record your screen activity\n   → Click 'Start Recording' to begin\n   → Click 'Stop Recording' when done\n\n2️⃣ Select a recording from your library\n   → Choose from 'Recording Library'\n   → Most recent appears first\n\n3️⃣ Choose your analysis type:\n   → Quick Analysis - Fast productivity insights\n   → Detailed Workflow - Step-by-step breakdown\n\n💡 Your AI-powered analysis will appear here with precise details about applications, actions, and workflow patterns.")

        analysis_tab_layout.addWidget(analysis_label)
        analysis_tab_layout.addWidget(self.analysis_text)

        # Voice Assistant Tab
        self.voice_assistant_widget = VoiceAssistantWidget(api_key=os.getenv("OPENAI_API_KEY"))

        # Add tabs
        self.right_tabs.addTab(analysis_tab, "📊 Video Analysis")
        self.right_tabs.addTab(self.voice_assistant_widget, "🎙️ Voice Assistant")

        right_layout.addWidget(self.right_tabs)

        # Add panels to splitter with optimized proportions
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([520, 680])
        content_splitter.setHandleWidth(3)

        # Add to main layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(content_splitter)

        self.setCentralWidget(main_widget)

    def apply_dark_styles(self):
        """Apply sophisticated dark styling"""
        # Main window style
        self.setStyleSheet(get_main_dark_stylesheet())

        # Text areas
        self.text.setStyleSheet(get_dark_text_area_stylesheet())
        self.analysis_text.setStyleSheet(get_dark_analysis_text_stylesheet())

        # Buttons
        buttons = [self.start_btn, self.stop_btn, self.screenshot_btn,
                  self.folder_btn, self.screenshots_folder_btn, self.analyses_folder_btn,
                  self.chart_btn, self.analyze_btn, self.workflow_btn, self.refresh_recordings_btn]

        for btn in buttons:
            btn.setStyleSheet(get_dark_button_stylesheet())
        
        # Recording list styling
        self.recordings_list.setStyleSheet(get_dark_text_area_stylesheet())

        # Labels
        self.title_label.setStyleSheet(get_dark_title_stylesheet())

        # Section labels
        section_labels = self.findChildren(QLabel)
        for label in section_labels:
            if label != self.title_label:
                label.setStyleSheet(get_dark_section_stylesheet())

        # Frames
        frames = self.findChildren(QFrame)
        for frame in frames:
            frame.setStyleSheet(get_dark_frame_stylesheet())

    def connect_signals(self):
        """Connect button signals to functions"""
        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.folder_btn.clicked.connect(self.open_recordings_folder)
        self.chart_btn.clicked.connect(self.show_chart)
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        self.screenshots_folder_btn.clicked.connect(self.open_screenshots_folder)
        self.analyses_folder_btn.clicked.connect(self.open_analyses_folder)
        self.analyze_btn.clicked.connect(self.analyze_video)
        self.workflow_btn.clicked.connect(self.analyze_workflow)
        self.refresh_recordings_btn.clicked.connect(self.refresh_recordings_list)

    def start_background_services(self):
        """Start activity tracking and hotkey listener"""
        start_tracking(self.db_conn)
        self.text.append("✓ Activity tracking initialized")

        start_hotkey_listener(self.on_hotkey_screenshot)
        self.text.append("✓ Hotkey listener active (Ctrl+Alt for screenshots)")

        # Populate recordings list
        self.refresh_recordings_list()

    def refresh_recordings_list(self):
        """Refresh the list of available recordings"""
        self.recordings_list.clear()
        recordings = video_analyzer.get_all_recordings()

        if not recordings:
            item = QListWidgetItem("📹 No recordings yet - create your first recording!")
            item.setData(Qt.UserRole, None)
            self.recordings_list.addItem(item)
            self.text.append("ℹ️ No recordings found in library")
            return

        for recording_path in recordings:
            filename = os.path.basename(recording_path)
            # Extract timestamp from filename
            try:
                timestamp_str = filename.replace("recording_", "").replace(".mp4", "")
                dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                display_name = f"🎬 {dt.strftime('%Y-%m-%d at %H:%M:%S')}"
            except:
                display_name = f"🎬 {filename}"

            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, recording_path)
            self.recordings_list.addItem(item)

        # Select the most recent (first in list)
        self.recordings_list.setCurrentRow(0)
        self.text.append(f"✓ Found {len(recordings)} recording{'s' if len(recordings) != 1 else ''}")
    
    def get_selected_recording(self):
        """Get the currently selected recording path"""
        current_item = self.recordings_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None

    def analyze_video(self):
        """Start video analysis in background thread"""
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.text.append("⚠️ Analysis already in progress")
            return

        selected_recording = self.get_selected_recording()
        if not selected_recording:
            self.text.append("⚠️ Please select a recording first")
            return

        self.analysis_text.setText("🤖 Analyzing video with AI...\n\nPlease wait while we process your recording...")
        self.analyze_btn.setEnabled(False)

        self.analysis_thread = AnalysisThread(selected_recording)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.start()

        recording_name = os.path.basename(selected_recording)
        self.text.append(f"🔄 Processing {recording_name} with AI...")

    def on_analysis_complete(self, analysis_result):
        """Handle completed video analysis"""
        if analysis_result and analysis_result.strip():
            self.analysis_text.setText(analysis_result)
            self.text.append("✅ Analysis completed successfully")
        else:
            self.analysis_text.setText("❌ No result received\n\nPlease verify your Claude API key is configured correctly.")
            self.text.append("❌ Analysis failed - check API configuration")

        self.analyze_btn.setEnabled(True)

    def analyze_workflow(self):
        """Start detailed workflow analysis in background thread"""
        if self.workflow_analysis_thread and self.workflow_analysis_thread.isRunning():
            self.text.append("⚠️ Workflow analysis already in progress")
            return

        selected_recording = self.get_selected_recording()
        if not selected_recording:
            self.text.append("⚠️ Please select a recording first")
            return

        self.analysis_text.setText("✨ Analyzing detailed workflow...\n\n🔍 Extracting actions from video frames\n⏱️ This may take 30-45 seconds\n\nPlease wait for comprehensive analysis...")
        self.workflow_btn.setEnabled(False)

        self.workflow_analysis_thread = WorkflowAnalysisThread(selected_recording)
        self.workflow_analysis_thread.analysis_complete.connect(self.on_workflow_analysis_complete)
        self.workflow_analysis_thread.start()

        recording_name = os.path.basename(selected_recording)
        self.text.append(f"🔄 Processing {recording_name} for detailed breakdown...")

    def on_workflow_analysis_complete(self, analysis_result, video_path):
        """Handle completed workflow analysis and save as package"""
        if analysis_result and analysis_result.strip():
            self.analysis_text.setText(analysis_result)
            self.text.append("✅ Detailed workflow analysis completed")

            # Save analysis package with video
            if video_path and os.path.exists(video_path):
                try:
                    package = video_analyzer.save_analysis_package(video_path, analysis_result)
                    if package:
                        self.text.append(f"💾 Saved: {package['title']}")
                        self.text.append(f"📂 Folder: {os.path.basename(package['folder'])}")
                        self.text.append(f"📝 Markdown: {os.path.basename(package['markdown'])}")
                        self.text.append(f"🎬 Video: {os.path.basename(package['video'])}")
                except Exception as e:
                    self.text.append(f"❌ Save error: {str(e)}")
        else:
            self.analysis_text.setText("❌ No result received\n\nPlease verify your Claude API key is configured correctly.")
            self.text.append("❌ Workflow analysis failed - check API configuration")

        self.workflow_btn.setEnabled(True)

    def start_recording(self):
        """Start screen recording."""
        if self.record_thread and self.record_thread.is_alive():
            self.text.append("⚠️ Recording already in progress")
            return

        filename = f"data/recordings/{timestamped_filename()}.mp4"
        self.stop_event = Event()
        self.record_thread = threading.Thread(
            target=record_screen,
            args=(filename, 3, self.stop_event)
        )
        self.record_thread.start()
        self.text.append(f"⏺️ Recording started → {os.path.basename(filename)}")

    def stop_recording(self):
        """Stop screen recording."""
        if self.stop_event and self.record_thread:
            self.stop_event.set()
            self.record_thread.join()
            self.text.append("⏹️ Recording stopped and saved")
            # Refresh recordings list to show new recording
            self.refresh_recordings_list()
        else:
            self.text.append("⚠️ No active recording to stop")

    def take_screenshot(self):
        """Take a screenshot manually."""
        from screenshot import capture_screenshot
        filename = capture_screenshot()
        if filename:
            self.text.append(f"📸 Screenshot saved → {os.path.basename(filename)}")
        else:
            self.text.append("❌ Screenshot failed")

    def on_hotkey_screenshot(self, filename):
        """Callback when hotkey screenshot is taken."""
        self.text.append(f"📸 Hotkey capture → {os.path.basename(filename)}")

    def open_recordings_folder(self):
        """Open recordings folder in file explorer."""
        recordings_path = os.path.abspath("data/recordings/")
        os.startfile(recordings_path)
        self.text.append("📁 Recordings folder opened")

    def open_screenshots_folder(self):
        """Open screenshots folder in file explorer."""
        screenshots_path = os.path.abspath("data/screenshots/")
        os.makedirs(screenshots_path, exist_ok=True)
        os.startfile(screenshots_path)
        self.text.append("🖼️ Screenshots folder opened")

    def open_analyses_folder(self):
        """Open analyses folder in file explorer."""
        analyses_path = os.path.abspath("data/analyses/")
        os.makedirs(analyses_path, exist_ok=True)
        os.startfile(analyses_path)
        self.text.append("📊 Analyses folder opened")

    def show_chart(self):
        """Show modern AI-themed usage chart."""
        cur = self.db_conn.cursor()
        cur.execute("""
            SELECT app, SUM(seconds) FROM usage
            WHERE date(timestamp) = date('now')
            GROUP BY app
            ORDER BY SUM(seconds) DESC
        """)
        rows = cur.fetchall()

        if not rows:
            self.text.append("ℹ️ No usage data available yet")
            return

        apps, secs = zip(*rows)
        mins = [s/60 for s in secs]

        # Modern AI app themed chart
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('#0a0e1a')

        # Modern gradient colors inspired by AI apps
        colors = ['#6478ff', '#7c88ff', '#9498ff', '#aca8ff', '#c4b8ff']
        bars = ax.bar(apps, mins, color=colors[:len(apps)], edgecolor='#8c98ff', linewidth=1.5)

        # Add gradient effect to bars
        for bar in bars:
            bar.set_alpha(0.85)

        ax.set_facecolor('#121829')
        ax.set_ylabel("Time (minutes)", fontsize=15, color='#e4e8f0', weight='normal', fontfamily='sans-serif')
        ax.set_title("Application Usage Analytics", fontsize=22, color='#ffffff', weight='600', pad=25, fontfamily='sans-serif')
        ax.tick_params(axis='x', rotation=45, colors='#d8dce6', labelsize=11)
        ax.tick_params(axis='y', colors='#d8dce6', labelsize=11)

        # Modern clean styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#6478ff')
        ax.spines['left'].set_alpha(0.3)
        ax.spines['bottom'].set_color('#6478ff')
        ax.spines['bottom'].set_alpha(0.3)
        ax.grid(True, alpha=0.15, color='#6478ff', linestyle='--')

        plt.tight_layout()
        plt.show()

        self.text.append("📈 Usage chart generated")


def run_gui():
    """Run the GUI application."""
    db_conn = init_db()
    app = QApplication(sys.argv)
    win = MainWindow(db_conn)
    win.show()
    sys.exit(app.exec_())