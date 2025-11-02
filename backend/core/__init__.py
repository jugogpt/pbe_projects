"""
Core managers for Activity Tracker AI backend
"""

from .recording_manager import recording_manager
from .screenshot_manager import screenshot_manager
from .tracker_manager import tracker_manager
from .analysis_manager import analysis_manager
from .voice_assistant_manager import voice_assistant_manager
from .workflow_manager import workflow_manager

__all__ = [
    'recording_manager',
    'screenshot_manager',
    'tracker_manager',
    'analysis_manager',
    'voice_assistant_manager',
    'workflow_manager'
]
