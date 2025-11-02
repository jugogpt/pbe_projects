"""Workflow Manager - Converts transcripts into actionable workflows using OpenAI GPT"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class WorkflowManager:
    def __init__(self):
        self.client = None
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("Workflow manager initialized with OpenAI")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
        else:
            print("WARNING: OPENAI_API_KEY not found in environment")
    
    def generate_workflow(self, transcript: str) -> Dict:
        """
        Convert a transcript into a concrete workflow using OpenAI GPT.
        The workflow describes actions a computer user takes on their system.
        """
        print(f"[WorkflowManager] Starting workflow generation for transcript (length: {len(transcript)} chars)")
        
        if not self.client:
            print("[WorkflowManager] ERROR: OpenAI client not initialized")
            return self._create_fallback_workflow(transcript, "OpenAI API not configured. Please set OPENAI_API_KEY in .env file")
        
        if not transcript or len(transcript.strip()) < 10:
            print("[WorkflowManager] ERROR: Transcript too short")
            return self._create_fallback_workflow(transcript, "Transcript is too short or empty")
        
        try:
            print(f"[WorkflowManager] Building prompt...")
            
            # Create a structured prompt for workflow generation
            prompt = f"""You are an expert at converting verbal descriptions into concrete, actionable workflows for computer automation.

The user has provided the following transcript describing their workflow:
"{transcript}"


Convert this into a structured, executable workflow. Format your response as a JSON object with the following structure:
{{
  "title": "A concise title for the workflow",
  "description": "Brief description of what this workflow does",
  "steps": [
    {{
      "step_number": 1,
      "action": "Action type (click, type, navigate, wait, etc.)",
      "target": "Description of what/where the action applies",
      "details": "Specific details or content",
      "automation_instruction": "Precise instruction for automation"
    }}
  ],
  "estimated_time": "Estimated completion time",
  "prerequisites": ["Any prerequisites or required state"],
  "automation_ready": true
}}

Be specific and technical. Each step should be automatable with tools like Selenium, PyAutoGUI, or similar automation frameworks.

IMPORTANT: Return ONLY the JSON object, no additional text before or after."""

            # Call OpenAI API with multiple model fallbacks
            print(f"[WorkflowManager] Calling OpenAI API...")
            model_names = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            message = None
            last_error = None
            
            for model_name in model_names:
                try:
                    print(f"Trying model: {model_name}")
                    # Add timeout and additional error handling
                    import time
                    start_time = time.time()
                    
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a workflow generation assistant. Always respond with valid JSON only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=2000,
                        temperature=0.3,
                        response_format={"type": "json_object"},
                        timeout=30  # 30 second timeout
                    )
                    
                    elapsed = time.time() - start_time
                    print(f"[WorkflowManager] API call completed in {elapsed:.2f} seconds")
                    
                    message = response.choices[0].message.content
                    print(f"[WorkflowManager] Response received, length: {len(message)} chars")
                    print(f"[WorkflowManager] Successfully used model: {model_name}")
                    break
                except Exception as e:
                    error_type = type(e).__name__
                    print(f"Model {model_name} failed ({error_type}): {str(e)}")
                    last_error = e
                    continue
            
            if message is None:
                raise Exception(f"All models failed. Last error: {last_error}")
            
            # Parse the JSON response
            print(f"[WorkflowManager] Parsing JSON response...")
            try:
                workflow = json.loads(message)
                print(f"[WorkflowManager] JSON parsed successfully")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                print(f"Response was: {message}")
                # Try to extract JSON from markdown code blocks if present
                if "```json" in message:
                    json_start = message.find("```json") + 7
                    json_end = message.find("```", json_start)
                    workflow = json.loads(message[json_start:json_end].strip())
                elif "```" in message:
                    json_start = message.find("```") + 3
                    json_end = message.find("```", json_start)
                    workflow = json.loads(message[json_start:json_end].strip())
                else:
                    raise Exception("Failed to parse JSON response")
            
            # Validate workflow structure
            if not isinstance(workflow, dict):
                raise Exception("Workflow is not a dictionary")
            
            # Ensure required fields exist
            if "title" not in workflow:
                workflow["title"] = "Generated Workflow"
            if "description" not in workflow:
                workflow["description"] = transcript[:100] + "..."
            if "steps" not in workflow:
                workflow["steps"] = []
            if "estimated_time" not in workflow:
                workflow["estimated_time"] = "Unknown"
            if "prerequisites" not in workflow:
                workflow["prerequisites"] = []
            if "automation_ready" not in workflow:
                workflow["automation_ready"] = True
            
            print(f"Successfully generated workflow: {workflow.get('title', 'Untitled')}")
            
            # Save workflow to file
            workflow_filepath = self._save_workflow_to_file(workflow, transcript)
            
            return {
                "transcript": transcript,
                "workflow": workflow,
                "workflow_file": workflow_filepath,
                "success": True
            }
            
        except Exception as e:
            print(f"Error generating workflow: {e}")
            error_msg = str(e)
            return self._create_fallback_workflow(transcript, error_msg)
    
    def _create_fallback_workflow(self, transcript: str, error_reason: str) -> Dict:
        """Create a fallback workflow when generation fails"""
        return {
            "transcript": transcript,
            "workflow": {
                "title": "Transcript Not Processed",
                "description": f"Could not generate workflow: {error_reason}",
                "steps": [
                    {
                        "step_number": 1,
                        "action": "note",
                        "target": "Transcript Content",
                        "details": transcript[:200] + "..." if len(transcript) > 200 else transcript,
                        "automation_instruction": "Manual review required - AI workflow generation failed"
                    }
                ],
                "estimated_time": "Unknown",
                "prerequisites": ["Manual review"],
                "automation_ready": False
            },
            "workflow_file": "",
            "success": False,
            "error": error_reason
        }
    
    def extract_key_terms(self, transcript: str) -> List[str]:
        """Extract key terms and actions from a transcript using OpenAI"""
        if not self.client:
            return []
        
        if not transcript:
            return []
        
        try:
            prompt = f"""Extract key terms, actions, and concepts from this transcript:
"{transcript}"

Return a JSON object with this structure:
{{
  "terms": ["term1", "term2", "term3"]
}}

Return ONLY the JSON object."""

            model_names = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            
            for model_name in model_names:
                try:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a data extraction assistant. Always respond with valid JSON only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=500,
                        temperature=0.3,
                        response_format={"type": "json_object"}
                    )
                    result = json.loads(response.choices[0].message.content)
                    return result.get("terms", [])
                except Exception:
                    continue
            
            return []
            
        except Exception as e:
            print(f"Error extracting terms: {e}")
            return []
    
    def generate_combined_workflow(self, voice_transcript: str, video_analysis: str) -> Dict:
        """
        Generate a combined workflow from both voice transcript and video analysis.
        Eliminates duplicate steps and merges information intelligently.
        """
        print(f"[WorkflowManager] Starting combined workflow generation")
        print(f"[WorkflowManager] Voice transcript length: {len(voice_transcript)} chars")
        print(f"[WorkflowManager] Video analysis length: {len(video_analysis)} chars")
        
        if not self.client:
            print("[WorkflowManager] ERROR: OpenAI client not initialized")
            return self._create_fallback_workflow(voice_transcript, "OpenAI API not configured")
        
        combined_input = f"""VOICE TRANSCRIPT:
{voice_transcript}

VIDEO ANALYSIS:
{video_analysis}"""
        
        try:
            prompt = f"""You are an expert at creating unified workflows from multiple information sources.

I have two sources of information about a user's workflow:
1. A voice transcript describing what the user intended to do
2. A video analysis showing what the user actually did

Combine these into a single, accurate workflow. Use the video analysis as the primary source for what actually happened, and the voice transcript for context, explanations, and intent.

IMPORTANT RULES:
- Eliminate duplicate steps that appear in both sources
- Keep only the most accurate and specific version of each action
- If the voice says one thing but the video shows something different, prioritize the video
- Merge related actions into single steps where appropriate
- Maintain chronological order

Format your response as a JSON object with this structure:
{{
  "title": "A concise title for the unified workflow",
  "description": "Brief description combining intent and execution",
  "steps": [
    {{
      "step_number": 1,
      "action": "Action type (click, type, navigate, wait, etc.)",
      "target": "Description of what/where the action applies",
      "details": "Specific details or content",
      "automation_instruction": "Precise instruction for automation",
      "source": "voice" or "video" or "combined"
    }}
  ],
  "estimated_time": "Estimated completion time",
  "prerequisites": ["Any prerequisites or required state"],
  "automation_ready": true
}}

Return ONLY the JSON object, no additional text before or after."""

            print(f"[WorkflowManager] Calling OpenAI API for combined workflow...")
            model_names = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            message = None
            last_error = None
            
            for model_name in model_names:
                try:
                    print(f"Trying model: {model_name}")
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a workflow generation assistant that merges multiple information sources. Always respond with valid JSON only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=3000,
                        temperature=0.3,
                        response_format={"type": "json_object"},
                        timeout=60
                    )
                    
                    message = response.choices[0].message.content
                    print(f"[WorkflowManager] Successfully used model: {model_name}")
                    break
                except Exception as e:
                    print(f"Model {model_name} failed: {str(e)}")
                    last_error = e
                    continue
            
            if message is None:
                raise Exception(f"All models failed. Last error: {last_error}")
            
            # Parse the JSON response
            print(f"[WorkflowManager] Parsing JSON response...")
            workflow = json.loads(message)
            
            # Ensure required fields exist
            if "title" not in workflow:
                workflow["title"] = "Combined Workflow"
            if "description" not in workflow:
                workflow["description"] = "Workflow generated from voice and video"
            if "steps" not in workflow:
                workflow["steps"] = []
            if "estimated_time" not in workflow:
                workflow["estimated_time"] = "Unknown"
            if "prerequisites" not in workflow:
                workflow["prerequisites"] = []
            if "automation_ready" not in workflow:
                workflow["automation_ready"] = True
            
            print(f"[WorkflowManager] Successfully generated combined workflow: {workflow.get('title', 'Untitled')}")
            
            # Save workflow to file
            workflow_filepath = self._save_combined_workflow_to_file(workflow, voice_transcript, video_analysis)
            
            return {
                "voice_transcript": voice_transcript,
                "video_analysis": video_analysis,
                "workflow": workflow,
                "workflow_file": workflow_filepath,
                "success": True
            }
            
        except Exception as e:
            print(f"Error generating combined workflow: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_workflow(voice_transcript, f"Combined workflow generation failed: {str(e)}")
    
    def _save_combined_workflow_to_file(self, workflow: Dict, voice_transcript: str, video_analysis: str) -> str:
        """Save combined workflow to a file"""
        try:
            # Create workflows directory if it doesn't exist
            workflows_dir = os.path.abspath("backend/data/workflows")
            os.makedirs(workflows_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_combined_{timestamp}.json"
            filepath = os.path.join(workflows_dir, filename)
            
            # Prepare workflow data with both sources
            workflow_data = {
                "generated_at": datetime.now().isoformat(),
                "source": "combined",
                "voice_transcript": voice_transcript,
                "video_analysis": video_analysis,
                "workflow": workflow
            }
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            
            print(f"Combined workflow saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving combined workflow to file: {e}")
            return ""
    
    def _save_workflow_to_file(self, workflow: Dict, transcript: str) -> str:
        """Save workflow to a file"""
        try:
            # Create workflows directory if it doesn't exist (use absolute path for persistence)
            workflows_dir = os.path.abspath("backend/data/workflows")
            os.makedirs(workflows_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_{timestamp}.json"
            filepath = os.path.join(workflows_dir, filename)
            
            # Prepare workflow data with transcript
            workflow_data = {
                "generated_at": datetime.now().isoformat(),
                "transcript": transcript,
                "workflow": workflow
            }
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            
            print(f"Workflow saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving workflow to file: {e}")
            return ""

workflow_manager = WorkflowManager()









