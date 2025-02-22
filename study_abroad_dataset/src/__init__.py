"""
Study Abroad Q&A Dataset Generator
A system for generating high-quality, diverse Q&A conversations about studying abroad.
"""

from .generator.conversation_generator import ConversationGenerator
from .generator.topic_manager import TopicManager
from .generator.quality_validator import QualityValidator
from .utils.config import Config
from .utils.logger import logger
from .utils.progress_tracker import ProgressTracker

__version__ = "1.0.0"
__author__ = "AI Assistant"

__all__ = [
    "ConversationGenerator",
    "TopicManager",
    "QualityValidator",
    "Config",
    "logger",
    "ProgressTracker",
]
