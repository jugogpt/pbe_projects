"""Activity Tracker Manager"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tracker import start_tracking
from utils import init_db

class TrackerManager:
    def __init__(self):
        self.db_conn = None
        self.tracking = False

    async def start(self):
        """Start activity tracking"""
        if not self.tracking:
            self.db_conn = init_db()
            start_tracking(self.db_conn)
            self.tracking = True
        return {"tracking": True}

    async def get_status(self):
        """Get tracking status"""
        return {"tracking": self.tracking}

    async def get_usage(self, date=None):
        """Get usage data"""
        if not self.db_conn:
            return {"error": "Tracking not started"}

        cur = self.db_conn.cursor()
        query = """
            SELECT app, SUM(seconds) as total_seconds
            FROM usage
            WHERE date(timestamp) = date(COALESCE(?, 'now'))
            GROUP BY app
            ORDER BY total_seconds DESC
        """
        cur.execute(query, (date,) if date else ('now',))
        rows = cur.fetchall()

        usage_data = [
            {"app": row[0], "seconds": row[1], "minutes": round(row[1] / 60, 2)}
            for row in rows
        ]

        return {"usage": usage_data, "count": len(usage_data)}

    async def get_chart_data(self):
        """Get data formatted for charts"""
        usage = await self.get_usage()
        if "error" in usage:
            return usage

        chart_data = {
            "labels": [item["app"] for item in usage["usage"]],
            "data": [item["minutes"] for item in usage["usage"]],
            "colors": ['#6478ff', '#7c88ff', '#9498ff', '#aca8ff', '#c4b8ff']
        }

        return chart_data

tracker_manager = TrackerManager()
