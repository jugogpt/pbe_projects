"""Screenshot Manager"""
import os
import asyncio
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from screenshot import capture_screenshot

class ScreenshotManager:
    async def capture(self):
        """Capture screenshot"""
        filename = capture_screenshot()
        return {
            "success": True if filename else False,
            "filename": os.path.basename(filename) if filename else None,
            "timestamp": datetime.now().isoformat()
        }

    async def list_screenshots(self):
        """List all screenshots"""
        screenshots_dir = "data/screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)

        screenshots = []
        for filename in os.listdir(screenshots_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(screenshots_dir, filename)
                stat = os.stat(filepath)
                screenshots.append({
                    "filename": filename,
                    "path": filepath,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })

        screenshots.sort(key=lambda x: x['created'], reverse=True)
        return {"screenshots": screenshots, "count": len(screenshots)}

screenshot_manager = ScreenshotManager()
