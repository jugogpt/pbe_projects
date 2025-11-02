# 🖥️ Activity Tracker + Screen Recorder App (Windows)

This project is a **Windows desktop application** that does two things:  
1. Tracks which applications you use and how long you use them.  
2. Records your screen (on demand) into lightweight MP4 files.  
3. Stores usage data in **SQLite** and shows charts of your activity.  

Later, the recordings and logs can be **plugged into an LLM** for analysis.

---

## 🚀 Features
- Tracks active applications and usage time in real-time.  
- Saves all activity into an **SQLite database** (`data/usage.db`).  
- Start/Stop screen recording with a GUI button.  
- Records at low FPS (configurable) for **small file sizes**.  
- Opens recordings folder directly from the app.  
- **Charts**: See daily app usage as bar plots in the GUI.
- **AI Video Analysis**: Get productivity insights from recordings (Claude API).
- **🆕 Detailed Workflow Analysis**: Hyperspecific step-by-step breakdown with app names, functions, and actions in numbered list format.  

---

## 🛠️ Tools & Libraries

### Core
- **Python 3.11+** (works best on Windows)  
- **pip** for package installs  

### Python Libraries
- `psutil` → get process info  
- `pywin32` → detect active window  
- `mss` → fast screen capture  
- `opencv-python` → encode video  
- `PyQt5` → GUI  
- `matplotlib` → charts in GUI  
- `sqlite3` → built-in Python library (no install needed)  

Install extras:  
```bash
pip install psutil pywin32 mss opencv-python PyQt5 matplotlib
```

---

## 📂 Project Structure

```
activity_tracker_app/
│
├── main.py              # Entry point (launches GUI)
├── tracker.py           # Tracks active apps + usage time (logs to SQLite)
├── recorder.py          # Screen recording logic
├── gui.py               # PyQt5 GUI (buttons, charts, integration)
├── utils.py             # Helper functions (folders, filenames, db init)
│
├── data/
│   ├── usage.db         # SQLite database
│   └── recordings/      # MP4 screen recordings
│
└── README.md            # This file
```

---

## ⚙️ Functions Overview

### `tracker.py`
- `get_active_app()` → returns current foreground process name.  
- `start_tracking(db_conn)` → runs in background, logs app usage into SQLite.  

### `recorder.py`
- `record_screen(output_file, fps, stop_event)` → starts screen capture loop until `stop_event` is set.  

### `gui.py`
- `MainWindow(QMainWindow)` → PyQt5 app window.  
  - **Start Recording** button → starts `recorder.py`.  
  - **Stop Recording** button → stops and saves video.  
  - **Open Folder** button → opens `data/recordings/`.  
  - **Show Chart** button → renders matplotlib bar chart of today’s usage.  

### `utils.py`
- `ensure_folders()` → creates `data/` and `data/recordings/`.  
- `timestamped_filename()` → generates unique MP4 filenames.  
- `init_db()` → sets up SQLite database with `usage` table.  

### `main.py`
- Entry point: initializes DB + tracker + GUI.  

---

## 🧩 Example Code Snippets

### tracker.py
```python
import time, psutil, win32gui, win32process
from threading import Thread

def get_active_app():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        return psutil.Process(pid).name()
    except psutil.NoSuchProcess:
        return None

def start_tracking(db_conn):
    cur = db_conn.cursor()
    last_app, last_time = None, time.time()

    def loop():
        nonlocal last_app, last_time
        while True:
            current = get_active_app()
            now = time.time()
            if current != last_app:
                if last_app:
                    elapsed = now - last_time
                    cur.execute(
                        "INSERT INTO usage (app, seconds, timestamp) VALUES (?, ?, datetime('now'))",
                        (last_app, elapsed),
                    )
                    db_conn.commit()
                last_app, last_time = current, now
            time.sleep(1)

    Thread(target=loop, daemon=True).start()
```

### utils.py
```python
import os, sqlite3, time

def ensure_folders():
    os.makedirs("data/recordings", exist_ok=True)

def timestamped_filename():
    return time.strftime("recording_%Y%m%d_%H%M%S")

def init_db():
    conn = sqlite3.connect("data/usage.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app TEXT,
            seconds REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    return conn
```

### gui.py
```python
import sys, os, threading
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from recorder import record_screen
from tracker import start_tracking
from utils import ensure_folders, timestamped_filename, init_db
from threading import Event
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self, db_conn):
        super().__init__()
        self.setWindowTitle("Activity Tracker + Recorder")
        ensure_folders()

        self.db_conn = db_conn
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)

        self.start_btn = QPushButton("Start Recording")
        self.stop_btn = QPushButton("Stop Recording")
        self.folder_btn = QPushButton("Open Recordings Folder")
        self.chart_btn = QPushButton("Show Today’s Usage Chart")

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.folder_btn)
        layout.addWidget(self.chart_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.folder_btn.clicked.connect(self.open_folder)
        self.chart_btn.clicked.connect(self.show_chart)

        start_tracking(self.db_conn)

        self.record_thread, self.stop_event = None, None

    def start_recording(self):
        filename = f"data/recordings/{timestamped_filename()}.mp4"
        self.stop_event = Event()
        self.record_thread = threading.Thread(target=record_screen, args=(filename, 3, self.stop_event))
        self.record_thread.start()
        self.text.append(f"Recording started → {filename}")

    def stop_recording(self):
        if self.stop_event:
            self.stop_event.set()
            self.record_thread.join()
            self.text.append("Recording stopped.")

    def open_folder(self):
        os.startfile("data/recordings/")

    def show_chart(self):
        cur = self.db_conn.cursor()
        cur.execute("""
            SELECT app, SUM(seconds) FROM usage
            WHERE date(timestamp) = date('now')
            GROUP BY app
        """)
        rows = cur.fetchall()
        if not rows:
            self.text.append("No data to plot yet.")
            return

        apps, secs = zip(*rows)
        plt.bar(apps, secs)
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Seconds")
        plt.title("Today’s App Usage")
        plt.tight_layout()
        plt.show()

def run_gui():
    db_conn = init_db()
    app = QApplication(sys.argv)
    win = MainWindow(db_conn)
    win.show()
    sys.exit(app.exec_())
```

### main.py
```python
from gui import run_gui

if __name__ == "__main__":
    run_gui()
```

---

## ▶️ Run the App
```bash
python main.py
```

You’ll see a GUI with:  
- Log of apps + time spent (saved to SQLite).  
- Start/Stop Recording buttons.  
- Open Folder button.  
- Show Chart button → bar graph of today’s app usage.  

---

## 📌 Next Steps
- Add **weekly/monthly charts** (aggregate usage).  
- Export data to **CSV/JSON**.  
- Integrate with **LLM pipeline** (summarize daily work).  
