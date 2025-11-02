import cv2
import mss
import numpy as np
import time
from threading import Event


def record_screen(output_file, fps=3, stop_event=None):
    """Record screen to MP4 file with configurable FPS."""
    if stop_event is None:
        stop_event = Event()

    # Initialize screen capture
    sct = mss.mss()
    monitor = sct.monitors[1]  # Primary monitor

    # Video codec and writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width = monitor["width"]
    height = monitor["height"]
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    frame_delay = 1.0 / fps

    try:
        while not stop_event.is_set():
            start_time = time.time()

            # Capture screen
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)

            # Convert from BGRA to BGR (remove alpha channel)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Write frame to video
            out.write(frame)

            # Control frame rate
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_delay - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except Exception as e:
        print(f"Recording error: {e}")
    finally:
        out.release()
        cv2.destroyAllWindows()