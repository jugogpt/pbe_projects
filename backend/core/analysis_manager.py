"""Video Analysis Manager with Workflow Generation"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from claude_api import video_analyzer
from core import workflow_manager

class AnalysisManager:
    async def analyze_video(self, video_path, detailed=False):
        """Analyze video with Claude AI and generate workflow"""
        try:
            # Convert to absolute path if relative
            if not os.path.isabs(video_path):
                # Try relative to backend directory first
                backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                potential_path = os.path.join(backend_dir, video_path)
                if os.path.exists(potential_path):
                    video_path = potential_path
                else:
                    # Try relative to current working directory
                    abs_path = os.path.abspath(video_path)
                    if os.path.exists(abs_path):
                        video_path = abs_path
            
            # Verify file exists
            if not os.path.exists(video_path):
                return {
                    "success": False,
                    "error": f"Video file not found: {video_path}",
                    "video_path": video_path
                }
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                video_analyzer.analyze_video_by_path,
                video_path,
                detailed
            )

            # Generate workflow from the analysis
            workflow_result = None
            if result and isinstance(result, str):
                try:
                    workflow_result = workflow_manager.generate_workflow(result)
                except Exception as e:
                    print(f"Error generating workflow from video analysis: {e}")

            return {
                "success": True,
                "analysis": result,
                "workflow": workflow_result,
                "video_path": video_path,
                "detailed": detailed
            }
        except Exception as e:
            return {"error": str(e), "success": False}

analysis_manager = AnalysisManager()
