"""
Recording Manager - Handles screen recording operations
"""

import os
import asyncio
from threading import Thread, Event
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from recorder import record_screen
from utils import timestamped_filename


class RecordingManager:
    """Manages screen recording operations"""

    def __init__(self):
        self.recording = False
        self.record_thread = None
        self.stop_event = None
        self.current_filename = None

    async def start_recording(self):
        """Start screen recording"""
        if self.recording:
            return {"error": "Recording already in progress", "recording": True}

        # Ensure recordings directory exists
        recordings_dir = os.path.abspath("data/recordings")
        os.makedirs(recordings_dir, exist_ok=True)
        
        # Generate filename with absolute path for persistence
        filename = f"{timestamped_filename()}.mp4"
        self.current_filename = os.path.join(recordings_dir, filename)
        self.stop_event = Event()

        # Start recording in background thread
        self.record_thread = Thread(
            target=record_screen,
            args=(self.current_filename, 3, self.stop_event),
            daemon=True
        )
        self.record_thread.start()
        self.recording = True

        return {
            "success": True,
            "recording": True,
            "filename": os.path.basename(self.current_filename),
            "timestamp": datetime.now().isoformat()
        }

    async def stop_recording(self):
        """Stop screen recording"""
        if not self.recording or not self.stop_event:
            return {"error": "No active recording", "recording": False}

        self.stop_event.set()
        if self.record_thread:
            self.record_thread.join(timeout=5)

        filename = os.path.basename(self.current_filename) if self.current_filename else None
        self.recording = False
        self.current_filename = None

        return {
            "success": True,
            "recording": False,
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }

    async def get_status(self):
        """Get current recording status"""
        return {
            "recording": self.recording,
            "current_file": os.path.basename(self.current_filename) if self.current_filename else None
        }

    async def list_recordings(self):
        """List all recordings"""
        recordings_dir = os.path.abspath("data/recordings")
        os.makedirs(recordings_dir, exist_ok=True)

        recordings = []
        for filename in os.listdir(recordings_dir):
            if filename.endswith('.mp4'):
                filepath = os.path.join(recordings_dir, filename)
                # Use absolute path for persistence
                abs_filepath = os.path.abspath(filepath)
                stat = os.stat(abs_filepath)

                recordings.append({
                    "filename": filename,
                    "path": abs_filepath,  # Always use absolute path
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        # Sort by creation time (newest first)
        recordings.sort(key=lambda x: x['created'], reverse=True)
        return {"recordings": recordings, "count": len(recordings)}


# Singleton instance
recording_manager = RecordingManager()
