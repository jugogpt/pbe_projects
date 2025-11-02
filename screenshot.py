import mss
import time
import os
import threading
import keyboard
from utils import ensure_folders


def capture_screenshot():
    """Capture a screenshot and save it to the screenshots folder."""
    ensure_folders()

    # Create screenshots folder if it doesn't exist
    screenshots_dir = "data/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    # Generate timestamped filename
    timestamp = time.strftime("screenshot_%Y%m%d_%H%M%S")
    filename = f"{screenshots_dir}/{timestamp}.png"

    try:
        # Capture screenshot
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filename)

        return filename
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None


def start_hotkey_listener(callback=None):
    """Start listening for Ctrl+Alt hotkey combination."""
    def on_hotkey():
        filename = capture_screenshot()
        if filename and callback:
            callback(filename)

    def hotkey_thread():
        try:
            # Register Ctrl+Alt hotkey
            keyboard.add_hotkey('ctrl+alt', on_hotkey)
            # Keep the thread alive
            keyboard.wait()
        except Exception as e:
            print(f"Hotkey error: {e}")

    # Start hotkey listener in a separate thread
    thread = threading.Thread(target=hotkey_thread, daemon=True)
    thread.start()
    return thread