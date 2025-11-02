"""
Advanced OpenAI Voice Assistant with Real-time Audio Processing
Continuous audio recording, transcription, and AI responses
"""

import os
import asyncio
import threading
import queue
from datetime import datetime
import json
from typing import Optional, Callable
import pyaudio
import wave
import tempfile

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class VoiceAssistant:
    """Advanced voice assistant with OpenAI Whisper and GPT-4"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the voice assistant"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Debug: Print to help diagnose issues
        if not self.api_key:
            print("DEBUG: No API key found!")
            print(f"DEBUG: Environment OPENAI_API_KEY = {os.getenv('OPENAI_API_KEY', 'NOT SET')}")
            raise ValueError("OpenAI API key is required. Please add OPENAI_API_KEY to your .env file")

        if OpenAI is None:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        # Initialize OpenAI client with error handling
        try:
            self.client = OpenAI(api_key=self.api_key)
            print("DEBUG: OpenAI client initialized successfully")
        except Exception as e:
            print(f"DEBUG: Failed to initialize OpenAI client: {str(e)}")
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 10  # Process every 10 seconds for better transcription accuracy

        # Audio components
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.device_index = None
        self.device_name = None

        # Callbacks
        self.on_transcript = None
        self.on_response = None
        self.on_error = None
        self.on_status = None
        self.on_partial_transcript = None  # For word-by-word updates
        self.on_final_transcript = None    # For final transcription
        self.on_word_detected = None       # For individual word detection
        self.on_audio_level = None         # For audio visualization (RMS level)
        self.on_device_info = None         # Callback for microphone device info

        # Conversation history
        self.conversation_history = []
        self.max_history = 20

        # Transcript storage
        self.transcript_file = self._create_transcript_file()
        
        # Audio level throttling
        self._last_audio_level_time = 0
        self._audio_level_throttle_ms = 50  # Throttle to every 50ms

    def _create_transcript_file(self):
        """Create a transcript file for the session"""
        os.makedirs("data/transcripts", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/transcripts/conversation_{timestamp}.txt"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Voice Assistant Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

        return filepath

    def _log_transcript(self, speaker: str, text: str):
        """Log transcript to file"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            with open(self.transcript_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {speaker}: {text}\n\n")
        except Exception as e:
            print(f"Error logging transcript: {e}")

    def _calculate_audio_level(self, audio_data):
        """Calculate RMS audio level for visualization with throttling"""
        try:
            import struct
            import math
            import time
            
            # Throttle audio level updates
            current_time = time.time() * 1000  # Convert to milliseconds
            if current_time - self._last_audio_level_time < self._audio_level_throttle_ms:
                return
            
            self._last_audio_level_time = current_time
            
            # Convert audio data to integers
            count = len(audio_data) // 2
            shorts = struct.unpack(f'<{count}h', audio_data)
            
            # Calculate RMS (Root Mean Square)
            sum_squares = sum(s * s for s in shorts)
            rms = math.sqrt(sum_squares / count) if count > 0 else 0
            
            # Normalize to 0-1 range (16-bit audio max is 32768)
            # More sensitive: divide by 500 instead of 1000 to catch quieter speech
            normalized_level = min(rms / 500.0, 1.0)
            
            # Debug: log if we have significant audio
            if normalized_level > 0.05:
                print(f"DEBUG: Audio detected - RMS: {rms:.2f}, Normalized: {normalized_level:.3f}")
            
            # Call the callback with the audio level
            if self.on_audio_level:
                self.on_audio_level(normalized_level)
        except Exception as e:
            print(f"DEBUG: Audio level calculation error: {e}")

    def start_recording(self):
        """Start continuous audio recording"""
        if self.recording:
            return

        try:
            # Get default input device info
            device_info = self.audio.get_default_input_device_info()
            self.device_index = device_info['index']
            self.device_name = device_info['name']
            
            print(f"Using microphone: {self.device_name} (index: {self.device_index})")
            
            # Send device info to callback
            if self.on_device_info:
                self.on_device_info(self.device_name)
            
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.CHUNK
            )
            self.recording = True

            if self.on_status:
                self.on_status("Recording started")

            # Start recording thread
            self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
            self.recording_thread.start()

        except Exception as e:
            print(f"Error starting recording: {e}")
            if self.on_error:
                self.on_error(f"Failed to start recording: {str(e)}")

    def stop_recording(self):
        """Stop audio recording"""
        self.recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.on_status:
            self.on_status("Recording stopped")

    def _recording_loop(self):
        """Continuous recording and processing loop"""
        print("Recording loop started")
        while self.recording:
            try:
                # Record audio chunk
                frames = []
                for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                    if not self.recording:
                        break
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)
                    
                    # Calculate audio level for visualization (with throttling)
                    if self.on_audio_level:
                        self._calculate_audio_level(data)

                if not self.recording:
                    break

                # Check if there's actual audio content (not just silence)
                has_audio = False
                import struct
                for frame_data in frames:
                    # Convert audio data to detect if there's actual audio
                    if len(frame_data) >= 2:
                        audio_samples = struct.unpack(f'<{len(frame_data)//2}h', frame_data)
                        rms = (sum(s**2 for s in audio_samples) / len(audio_samples)) ** 0.5 if audio_samples else 0
                        if rms > 20:  # Threshold for detecting actual audio
                            has_audio = True
                            break
                
                # Only process if there's actual audio content
                if not has_audio and len(frames) > 0:
                    print("No audio detected in this chunk, skipping...")
                    continue

                print(f"Recorded {len(frames)} chunks ({self.RECORD_SECONDS}s), processing...")

                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                    wf = wave.open(temp_audio.name, 'wb')
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()

                    # Process the audio
                    self._process_audio(temp_audio.name)

                    # Clean up temp file
                    try:
                        os.unlink(temp_audio.name)
                    except:
                        pass

            except Exception as e:
                print(f"Recording error in loop: {e}")
                if self.on_error and self.recording:
                    self.on_error(f"Recording error: {str(e)}")

    def _process_audio(self, audio_file: str):
        """Process audio file with OpenAI Whisper"""
        try:
            # Check if file has content
            file_size = os.path.getsize(audio_file)
            print(f"Processing audio file: {audio_file}, size: {file_size} bytes")
            
            if file_size < 1000:  # Skip very small files
                print("Audio file too small, skipping")
                return

            # Transcribe audio
            print("Calling Whisper API...")
            with open(audio_file, 'rb') as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"
                )
            
            text = transcript.text.strip()
            print(f"Whisper returned text: '{text}'")

            # Ignore empty or very short transcripts
            if len(text) < 3:
                print("Transcribed text too short, ignoring")
                return

            # Simulate word-by-word display for smooth, live transcription
            # Split text into words and display them one by one
            words = text.split()
            print(f"Processing {len(words)} words for display")

            import time
            for i, word in enumerate(words):
                # Send individual word as it's detected (for smooth frontend display)
                if self.on_word_detected:
                    self.on_word_detected(word)
                
                # Continuously update partial transcript for smooth, live display
                partial_text = ' '.join(words[:i+1])
                if self.on_partial_transcript:
                    self.on_partial_transcript(partial_text)
                
                # Very fast delay for smooth animation (5-10ms per word)
                time.sleep(0.01 + (len(word) * 0.005))  # 10-20ms per word depending on length

            # Log transcript
            self._log_transcript("User", text)

            # Notify transcript callback with final text
            if self.on_transcript:
                self.on_transcript(text)
            
            # Notify final transcript callback
            if self.on_final_transcript:
                self.on_final_transcript(text)

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": text
            })

            # NOTE: AI workflow generation happens when recording stops, 
            # not after each individual transcription chunk

        except Exception as e:
            print(f"Error processing audio: {e}")
            import traceback
            traceback.print_exc()
            if self.on_error:
                self.on_error(f"Processing error: {str(e)}")

    def _generate_response(self):
        """Generate AI response using GPT-4"""
        try:
            # Prepare messages with system prompt
            messages = [
                {
                    "role": "system",
                    "content": """You are an intelligent voice assistant integrated into an activity tracking application.
                    You help users by:
                    - Providing insights about their screen recordings and activity
                    - Answering questions about productivity
                    - Offering helpful suggestions
                    - Being concise and clear in your responses

                    Keep responses brief and conversational (2-3 sentences max unless asked for detail)."""
                }
            ]

            # Add recent conversation history
            messages.extend(self.conversation_history[-self.max_history:])

            # Get response from GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()

            # Log AI response
            self._log_transcript("Assistant", ai_response)

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })

            # Notify response callback
            if self.on_response:
                self.on_response(ai_response)

        except Exception as e:
            if self.on_error:
                self.on_error(f"Response generation error: {str(e)}")

    def send_text_message(self, text: str):
        """Send a text message and get response"""
        try:
            # Log user message
            self._log_transcript("User", text)

            # Notify transcript callback
            if self.on_transcript:
                self.on_transcript(text)

            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": text
            })

            # Generate response
            self._generate_response()

        except Exception as e:
            if self.on_error:
                self.on_error(f"Text message error: {str(e)}")

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        if self.on_status:
            self.on_status("Conversation history cleared")

    def get_transcript_file_path(self):
        """Get the current transcript file path"""
        return self.transcript_file

    def cleanup(self):
        """Cleanup resources"""
        self.stop_recording()
        self.audio.terminate()
