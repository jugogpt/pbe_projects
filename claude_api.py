"""
Claude API integration for video analysis
"""

import os
import requests
import base64
import json
import shutil
from glob import glob
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()


class VideoAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            print("Warning: No Claude API key found. Set ANTHROPIC_API_KEY environment variable.")

        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

    def get_latest_recording(self):
        """Get the most recent recording file"""
        recordings_dir = "data/recordings"
        if not os.path.exists(recordings_dir):
            return None

        # Get all MP4 files and sort by modification time
        mp4_files = glob(os.path.join(recordings_dir, "*.mp4"))
        if not mp4_files:
            return None

        # Return the most recently modified file
        latest_file = max(mp4_files, key=os.path.getmtime)
        return latest_file

    def extract_video_frames(self, video_path, num_frames=5):
        """Extract frames from video for analysis"""
        try:
            import cv2

            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames == 0:
                return []

            # Extract frames at even intervals
            frame_indices = [int(i * total_frames / (num_frames + 1)) for i in range(1, num_frames + 1)]
            frames = []

            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    # Convert frame to base64
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    frames.append(frame_b64)

            cap.release()
            return frames

        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []

    def analyze_video(self, video_path):
        """Analyze video content using Claude API"""
        if not self.api_key:
            return "Claude API key not configured. Please set ANTHROPIC_API_KEY environment variable."

        if not video_path or not os.path.exists(video_path):
            return "No video file found to analyze."

        # Extract frames from video
        frames = self.extract_video_frames(video_path, num_frames=3)

        if not frames:
            return "Could not extract frames from video for analysis."

        # Prepare the message for Claude
        content = [
            {
                "type": "text",
                "text": """Analyze this screen recording and provide a concise summary of the user's activity.
                Focus on:
                - What applications or websites were being used
                - What tasks or activities the user was performing
                - Any notable patterns or workflows observed
                - Productivity insights or recommendations

                Keep the summary professional and under 200 words."""
            }
        ]

        # Add frames to the content
        for i, frame in enumerate(frames):
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": frame
                }
            })

        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                print(error_msg)
                return f"Analysis failed: {error_msg}"

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(error_msg)
            return f"Analysis failed: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return f"Analysis failed: {error_msg}"

    def analyze_latest_recording(self):
        """Analyze the most recent recording"""
        latest_file = self.get_latest_recording()
        if not latest_file:
            return "No recordings found to analyze."

        filename = os.path.basename(latest_file)
        analysis = self.analyze_video(latest_file)

        return f"Analysis of {filename}:\n\n{analysis}"

    def analyze_workflow_detailed(self, video_path):
        """Analyze video with hyperspecific workflow details"""
        if not self.api_key:
            return "Claude API key not configured. Please set ANTHROPIC_API_KEY environment variable."

        if not video_path or not os.path.exists(video_path):
            return "No video file found to analyze."

        # Extract more frames for detailed analysis (5 frames)
        frames = self.extract_video_frames(video_path, num_frames=5)

        if not frames:
            return "Could not extract frames from video for analysis."

        # Hyperspecific prompt for detailed workflow
        content = [
            {
                "type": "text",
                "text": """Analyze this screen recording and provide a HYPERSPECIFIC, DETAILED workflow breakdown.

                Create a numbered list that captures EVERY action, with exact details:

                For each step, include:
                - Exact application name (e.g., "Visual Studio Code", "Google Chrome", "File Explorer")
                - Specific feature/function used (e.g., "Find and Replace dialog", "Developer Tools", "Address Bar")
                - Precise action taken (e.g., "clicked Search button", "typed 'index.html'", "pressed Ctrl+S")
                - Any visible text, file names, or UI elements interacted with

                Format your response as:
                1. [App Name] - [Function/Feature] - [Specific Action]
                2. [App Name] - [Function/Feature] - [Specific Action]
                ...

                Example format:
                1. Google Chrome - Address Bar - Typed "github.com"
                2. Google Chrome - Navigation - Pressed Enter key
                3. Visual Studio Code - File Explorer Panel - Clicked "src" folder
                4. Visual Studio Code - Editor Window - Opened "main.py" file
                5. Visual Studio Code - Editor - Typed "import sys" on line 1

                Be extremely detailed and specific. Capture every observable action, click, keystroke, and navigation."""
            }
        ]

        # Add frames to the content
        for i, frame in enumerate(frames):
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": frame
                }
            })

        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1500,  # Increased for detailed output
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=45
            )

            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                print(error_msg)
                return f"Analysis failed: {error_msg}"

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(error_msg)
            return f"Analysis failed: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return f"Analysis failed: {error_msg}"

    def analyze_latest_workflow(self):
        """Analyze the most recent recording with detailed workflow breakdown"""
        latest_file = self.get_latest_recording()
        if not latest_file:
            return "No recordings found to analyze."

        filename = os.path.basename(latest_file)
        analysis = self.analyze_workflow_detailed(latest_file)

        return f"DETAILED WORKFLOW ANALYSIS - {filename}\n\n{analysis}"

    def get_all_recordings(self):
        """Get list of all recording files"""
        recordings_dir = "data/recordings"
        if not os.path.exists(recordings_dir):
            return []

        # Get all MP4 files and sort by modification time (newest first)
        mp4_files = glob(os.path.join(recordings_dir, "*.mp4"))
        if not mp4_files:
            return []

        # Sort by modification time, newest first
        mp4_files.sort(key=os.path.getmtime, reverse=True)
        return mp4_files

    def analyze_video_by_path(self, video_path, detailed=True):
        """Analyze a specific video file by path"""
        if not video_path or not os.path.exists(video_path):
            return "Video file not found."

        filename = os.path.basename(video_path)
        
        if detailed:
            analysis = self.analyze_workflow_detailed(video_path)
            return f"DETAILED WORKFLOW ANALYSIS - {filename}\n\n{analysis}"
        else:
            analysis = self.analyze_video(video_path)
            return f"Analysis of {filename}:\n\n{analysis}"

    def generate_title_for_analysis(self, analysis_text):
        """Generate a concise title for the analysis using AI"""
        if not self.api_key:
            # Fallback title if no API key
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"Analysis_{timestamp}"

        # Create a short prompt to generate a title
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": f"Based on this workflow analysis, generate a short, descriptive title (3-6 words, no special characters except hyphens and underscores). Just return the title, nothing else:\n\n{analysis_text[:500]}"
                }
            ]
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                title = result["content"][0]["text"].strip()
                # Clean title for filename
                title = title.replace('"', '').replace("'", "").replace(':', '-')
                title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
                title = title.replace(' ', '_')
                return title[:80]  # Limit length
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return f"Analysis_{timestamp}"
        except Exception as e:
            print(f"Title generation error: {e}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"Analysis_{timestamp}"

    def save_analysis_package(self, video_path, analysis_text, title=None):
        """Save analysis as markdown and package with video in organized folder"""
        if not video_path or not os.path.exists(video_path):
            return None

        # Generate title if not provided
        if not title:
            title = self.generate_title_for_analysis(analysis_text)

        # Create analyses directory
        analyses_dir = "data/analyses"
        os.makedirs(analyses_dir, exist_ok=True)

        # Create timestamped folder for this analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{timestamp}_{title}"
        analysis_folder = os.path.join(analyses_dir, folder_name)
        os.makedirs(analysis_folder, exist_ok=True)

        # Copy video to analysis folder
        video_filename = os.path.basename(video_path)
        video_dest = os.path.join(analysis_folder, video_filename)
        shutil.copy2(video_path, video_dest)

        # Save analysis as markdown
        md_filename = f"{title}.md"
        md_path = os.path.join(analysis_folder, md_filename)
        
        # Format markdown with title
        markdown_content = f"# {title.replace('_', ' ')}\n\n"
        markdown_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown_content += f"**Source Video:** {video_filename}\n\n"
        markdown_content += "---\n\n"
        markdown_content += analysis_text
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return {
            'folder': analysis_folder,
            'markdown': md_path,
            'video': video_dest,
            'title': title
        }


# Global analyzer instance
video_analyzer = VideoAnalyzer()