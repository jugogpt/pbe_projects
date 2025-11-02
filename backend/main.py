"""
FastAPI Backend for Activity Tracker AI
Modern REST API + WebSocket server for Electron frontend
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import core modules
from core import (
    recording_manager,
    screenshot_manager,
    tracker_manager,
    analysis_manager,
    voice_assistant_manager,
    workflow_manager
)

# Initialize FastAPI app
app = FastAPI(
    title="Activity Tracker AI API",
    description="Backend API for modern activity tracking and AI analysis",
    version="2.0.0"
)

# CORS middleware for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Set up voice assistant manager with WebSocket broadcast capability
async def voice_broadcast(message: dict):
    """Broadcast function for voice assistant real-time updates"""
    await manager.broadcast(message)

voice_assistant_manager.set_ws_broadcast(voice_broadcast)


# Pydantic models
class RecordingControl(BaseModel):
    action: str  # "start" or "stop"
    filename: Optional[str] = None


class AnalysisRequest(BaseModel):
    video_path: str
    detailed: bool = False


class VoiceMessage(BaseModel):
    text: str


class UsageQuery(BaseModel):
    date: Optional[str] = None


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Activity Tracker AI Backend",
        "version": "2.0.0",
        "status": "running"
    }


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ===== Recording Endpoints =====

@app.post("/api/recording/start")
async def start_recording():
    """Start screen recording"""
    try:
        result = await recording_manager.start_recording()
        await manager.broadcast({
            "type": "recording_started",
            "data": result
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recording/stop")
async def stop_recording():
    """Stop screen recording"""
    try:
        result = await recording_manager.stop_recording()
        await manager.broadcast({
            "type": "recording_stopped",
            "data": result
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recording/status")
async def get_recording_status():
    """Get current recording status"""
    return await recording_manager.get_status()


@app.get("/api/recordings/list")
async def list_recordings():
    """List all available recordings"""
    return await recording_manager.list_recordings()


# ===== Screenshot Endpoints =====

@app.post("/api/screenshot/capture")
async def capture_screenshot():
    """Capture a screenshot"""
    try:
        result = await screenshot_manager.capture()
        await manager.broadcast({
            "type": "screenshot_captured",
            "data": result
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/screenshots/list")
async def list_screenshots():
    """List all screenshots"""
    return await screenshot_manager.list_screenshots()


# ===== Activity Tracking Endpoints =====

@app.get("/api/activity/status")
async def get_activity_status():
    """Get activity tracking status"""
    return await tracker_manager.get_status()


@app.post("/api/activity/start")
async def start_activity_tracking():
    """Start activity tracking"""
    result = await tracker_manager.start()
    return result


@app.get("/api/activity/usage")
async def get_usage_data(date: Optional[str] = None):
    """Get usage statistics"""
    return await tracker_manager.get_usage(date)


@app.get("/api/activity/chart-data")
async def get_chart_data():
    """Get data for usage charts"""
    return await tracker_manager.get_chart_data()


# ===== Video Analysis Endpoints =====

@app.post("/api/analysis/quick")
async def quick_analysis(request: AnalysisRequest):
    """Run quick video analysis"""
    try:
        # Send progress update
        await manager.broadcast({
            "type": "analysis_started",
            "data": {"video_path": request.video_path}
        })

        result = await analysis_manager.analyze_video(
            request.video_path,
            detailed=False
        )

        await manager.broadcast({
            "type": "analysis_complete",
            "data": result
        })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analysis/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file to the recordings directory"""
    try:
        # Ensure recordings directory exists with absolute path
        recordings_dir = os.path.abspath("data/recordings")
        os.makedirs(recordings_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        filepath = os.path.join(recordings_dir, filename)
        
        # Save uploaded file
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "success": True,
            "filename": filename,
            "path": filepath,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analysis/detailed")
async def detailed_analysis(request: AnalysisRequest):
    """Run detailed workflow analysis"""
    try:
        await manager.broadcast({
            "type": "analysis_started",
            "data": {"video_path": request.video_path, "detailed": True}
        })

        result = await analysis_manager.analyze_video(
            request.video_path,
            detailed=True
        )

        # Broadcast workflow if available
        if result.get("workflow"):
            await manager.broadcast({
                "type": "workflow_generated",
                "data": result["workflow"]
            })

        await manager.broadcast({
            "type": "analysis_complete",
            "data": result
        })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Voice Assistant Endpoints =====

@app.post("/api/voice/start")
async def start_voice_assistant():
    """Start voice recording"""
    try:
        result = await voice_assistant_manager.start_recording()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/stop")
async def stop_voice_assistant():
    """Stop voice recording"""
    try:
        result = await voice_assistant_manager.stop_recording()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/message")
async def send_voice_message(message: VoiceMessage):
    """Send text message to voice assistant"""
    try:
        result = await voice_assistant_manager.send_message(message.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/transcripts")
async def get_transcripts():
    """Get list of transcript files"""
    return await voice_assistant_manager.get_transcripts()


@app.post("/api/workflow/generate")
async def generate_workflow(request: dict):
    """Generate a workflow from a transcript"""
    transcript = request.get("transcript", "")
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")
    
    workflow_result = workflow_manager.generate_workflow(transcript)
    
    # Broadcast workflow result via WebSocket
    await manager.broadcast({
        "type": "workflow_generated",
        "data": workflow_result
    })
    
    return workflow_result


# ===== File Management Endpoints =====

@app.get("/api/files/recordings/{filename}")
async def get_recording_file(filename: str):
    """Download a recording file"""
    file_path = os.path.join("data", "recordings", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/api/files/screenshots/{filename}")
async def get_screenshot_file(filename: str):
    """Download a screenshot file"""
    file_path = os.path.join("data", "screenshots", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


# ===== WebSocket Endpoint =====

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_message({"type": "pong"}, websocket)

            elif message.get("type") == "voice_transcript":
                # Broadcast voice transcripts to all clients
                await manager.broadcast({
                    "type": "voice_transcript",
                    "data": message.get("data")
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ===== System Management =====

@app.get("/api/system/folders")
async def get_folder_paths():
    """Get system folder paths"""
    return {
        "recordings": os.path.abspath("data/recordings"),
        "screenshots": os.path.abspath("data/screenshots"),
        "analyses": os.path.abspath("data/analyses"),
        "transcripts": os.path.abspath("data/transcripts")
    }


@app.post("/api/system/open-folder")
async def open_folder(folder: dict):
    """Open a folder in file explorer"""
    folder_path = folder.get("path")
    if os.path.exists(folder_path):
        os.startfile(folder_path)
        return {"success": True}
    raise HTTPException(status_code=404, detail="Folder not found")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize all managers on startup"""
    print("🚀 Starting Activity Tracker AI Backend...")

    # Initialize database and folders
    from utils import ensure_folders, init_db
    ensure_folders()

    # Start activity tracking
    await tracker_manager.start()

    print("✅ Backend ready on http://127.0.0.1:5000")


# Run server
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        log_level="info"
    )
