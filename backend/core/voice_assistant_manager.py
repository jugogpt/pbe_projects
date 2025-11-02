"""Voice Assistant Manager"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Callable, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from voice_assistant import VoiceAssistant

class VoiceAssistantManager:
    def __init__(self):
        self.assistant = None
        self.recording = False
        self.callbacks: List[Callable] = []
        self.ws_broadcast: Optional[Callable] = None
        self._current_audio_level = 0.0
        self._audio_broadcast_task = None
        self._transcript_history = []  # Store all transcripts for workflow generation

    def set_ws_broadcast(self, broadcast_fn: Callable):
        """Set WebSocket broadcast function for real-time updates"""
        self.ws_broadcast = broadcast_fn

    async def _broadcast_transcript(self, message_type: str, data: dict):
        """Broadcast transcript event to all connected clients"""
        if self.ws_broadcast:
            try:
                await self.ws_broadcast({
                    "type": message_type,
                    "data": data
                })
            except Exception as e:
                print(f"Error broadcasting transcript: {e}")

    async def initialize(self):
        """Initialize voice assistant"""
        if not self.assistant:
            api_key = os.getenv("OPENAI_API_KEY")
            self.assistant = VoiceAssistant(api_key=api_key)
            
            # Set up callbacks for real-time updates (sync wrappers for async broadcast)
            def on_partial_transcript(text: str):
                """Called when partial transcription is received"""
                # Schedule broadcast in a thread-safe way
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(self._broadcast_transcript("partial_transcript", {"text": text}), loop)
                except RuntimeError:
                    # If no loop, just skip
                    pass
            
            def on_final_transcript(text: str):
                """Called when final transcription is received"""
                # Store transcript for later workflow generation
                if text and len(text) > 5:
                    self._transcript_history.append(text)
                
                # Schedule broadcast in a thread-safe way
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(self._broadcast_transcript("final_transcript", {"text": text}), loop)
                except RuntimeError:
                    pass
            
            def on_word_detected(word: str):
                """Called when a word is detected during recording"""
                # Schedule broadcast in a thread-safe way  
                try:
                    if hasattr(self, '_word_buffer'):
                        self._word_buffer.append(word)
                    else:
                        self._word_buffer = [word]
                except:
                    pass
            
            def on_audio_level(level: float):
                """Called when audio level is calculated for visualization"""
                # Store the audio level - it will be broadcast by background task
                self._current_audio_level = level
            
            def on_device_info(device_name: str):
                """Called when microphone device is detected"""
                # Schedule broadcast in a thread-safe way
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(self._broadcast_transcript("device_info", {"device_name": device_name}), loop)
                except RuntimeError:
                    pass
            
            self.assistant.on_partial_transcript = on_partial_transcript
            self.assistant.on_final_transcript = on_final_transcript
            self.assistant.on_word_detected = on_word_detected
            self.assistant.on_audio_level = on_audio_level
            self.assistant.on_device_info = on_device_info
            
        return {"initialized": True}

    async def start_recording(self):
        """Start voice recording"""
        if not self.assistant:
            await self.initialize()

        # Clear transcript history at start of new recording
        self._transcript_history = []
        self._word_buffer = []  # Initialize word buffer
        
        self.assistant.start_recording()
        self.recording = True
        await self._broadcast_transcript("recording_started", {"timestamp": datetime.now().isoformat()})
        
        # Start audio level broadcasting task
        self._audio_broadcast_task = asyncio.create_task(self._broadcast_audio_levels())
        
        return {"recording": True}
    
    async def _broadcast_audio_levels(self):
        """Background task to broadcast audio levels and words periodically"""
        self._word_buffer = []  # Initialize word buffer
        while self.recording:
            # Broadcast audio level
            if self._current_audio_level > 0:
                await self._broadcast_transcript("audio_level", {"level": self._current_audio_level})
            
            # Broadcast any pending words
            if hasattr(self, '_word_buffer') and self._word_buffer:
                for word in self._word_buffer:
                    await self._broadcast_transcript("word_detected", {"word": word, "timestamp": datetime.now().isoformat()})
                self._word_buffer = []  # Clear after broadcasting
            
            await asyncio.sleep(0.05)  # Broadcast every 50ms for smoother updates

    async def stop_recording(self):
        """Stop voice recording"""
        if self.assistant:
            self.assistant.stop_recording()
        self.recording = False
        self._current_audio_level = 0.0
        
        # Stop audio level broadcasting task
        if self._audio_broadcast_task:
            self._audio_broadcast_task.cancel()
            try:
                await self._audio_broadcast_task
            except asyncio.CancelledError:
                pass
        
        # Clear transcript history for next recording first
        transcript_to_process = " ".join(self._transcript_history) if self._transcript_history else ""
        self._transcript_history = []
        
        # Immediately return response to unblock the stop button
        await self._broadcast_transcript("recording_stopped", {"timestamp": datetime.now().isoformat()})
        
        # Generate workflow in background (don't await to avoid blocking)
        if transcript_to_process and len(transcript_to_process) > 10:
            asyncio.create_task(self._generate_workflow_from_transcript(transcript_to_process))
        
        return {"recording": False}
    
    async def _generate_workflow_from_transcript(self, transcript: str):
        """Generate workflow from full accumulated transcript"""
        try:
            print(f"Generating workflow from transcript (length: {len(transcript)} chars)")
            
            # Send initial progress update
            await self._broadcast_transcript("workflow_progress", {"stage": "starting", "message": "Initializing workflow generation..."})
            
            from core import workflow_manager
            
            # Send progress update
            await self._broadcast_transcript("workflow_progress", {"stage": "processing", "message": "Analyzing transcript with AI..."})
            
            # Generate workflow with improved error handling
            workflow_result = workflow_manager.generate_workflow(transcript)
            
            # Send progress update
            await self._broadcast_transcript("workflow_progress", {"stage": "formatting", "message": "Formatting workflow structure..."})
            
            # Log the result
            if workflow_result.get("success", False):
                print(f"Workflow generated successfully: {workflow_result.get('workflow', {}).get('title', 'Unknown')}")
                if workflow_result.get("workflow_file"):
                    print(f"Workflow saved to: {workflow_result['workflow_file']}")
            else:
                print(f"Workflow generation failed: {workflow_result.get('error', 'Unknown error')}")
            
            # Broadcast the result to frontend
            await self._broadcast_transcript("workflow_progress", {"stage": "completed", "message": "Workflow generation complete!"})
            await self._broadcast_transcript("workflow_generated", workflow_result)
            
        except Exception as e:
            print(f"Error in workflow generation pipeline: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error progress
            await self._broadcast_transcript("workflow_progress", {"stage": "error", "message": f"Error: {str(e)}"})
            
            # Send error to frontend
            await self._broadcast_transcript("workflow_generated", {
                "success": False,
                "error": str(e),
                "workflow": {
                    "title": "Error",
                    "description": f"Failed to generate workflow: {str(e)}",
                    "steps": [],
                    "estimated_time": "Unknown",
                    "automation_ready": False
                }
            })

    async def send_message(self, text):
        """Send text message"""
        if not self.assistant:
            await self.initialize()

        self.assistant.send_text_message(text)
        return {"sent": True, "message": text}

    async def get_transcripts(self):
        """Get transcript files"""
        transcripts_dir = "data/transcripts"
        os.makedirs(transcripts_dir, exist_ok=True)

        transcripts = []
        for filename in os.listdir(transcripts_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(transcripts_dir, filename)
                stat = os.stat(filepath)
                transcripts.append({
                    "filename": filename,
                    "path": filepath,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })

        transcripts.sort(key=lambda x: x['created'], reverse=True)
        return {"transcripts": transcripts, "count": len(transcripts)}

voice_assistant_manager = VoiceAssistantManager()
