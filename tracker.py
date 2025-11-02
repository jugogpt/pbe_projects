import time
import psutil
import win32gui
import win32process
from threading import Thread


def get_active_app():
    """Get the name of the currently active application."""
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        return psutil.Process(pid).name()
    except psutil.NoSuchProcess:
        return None


def start_tracking(db_conn):
    """Start tracking active applications and log usage to database."""
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