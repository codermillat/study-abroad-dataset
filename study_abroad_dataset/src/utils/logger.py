"""
Enhanced logging module for the study abroad dataset generation system.
Provides structured logging with detailed formatting and multiple outputs.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from .config import Config

class Logger:
    """
    Enhanced logger with support for both file and console output,
    structured formatting, and different log levels for different handlers.
    """
    
    def __init__(self, name: str = "DatasetGenerator"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        self.log_dir = Config.BASE_DIR / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"generation_{timestamp}.log"
        
        # Clear any existing handlers
        self.logger.handlers = []
        
        # Set up handlers
        self._setup_console_handler()
        self._setup_file_handler()
        
        self.logger.info("Logger initialized")
    
    def _setup_console_handler(self):
        """Set up console handler with color formatting"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create colored formatter
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Set up file handler with detailed formatting"""
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create detailed formatter
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def _log_with_context(self, level: int, message: str, context: Optional[dict] = None):
        """Log message with additional context if provided"""
        if context:
            message = f"{message} | Context: {context}"
        self.logger.log(level, message)
    
    def debug(self, message: str, context: Optional[dict] = None):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[dict] = None):
        """Log info message"""
        self._log_with_context(logging.INFO, message, context)
    
    def warning(self, message: str, context: Optional[dict] = None):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, context)
    
    def error(self, message: str, context: Optional[dict] = None):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, context)
    
    def critical(self, message: str, context: Optional[dict] = None):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, context)
    
    def progress(self, current: int, total: int, topic: Optional[str] = None):
        """Log generation progress"""
        percentage = (current / total) * 100
        message = f"Progress: {current}/{total} ({percentage:.1f}%)"
        if topic:
            message += f" | Topic: {topic}"
        self.info(message)
    
    def topic_summary(self, topic_counts: dict):
        """Log topic distribution summary"""
        self.info("Topic Distribution Summary:")
        for topic, count in topic_counts.items():
            self.info(f"  - {topic}: {count} conversations")
    
    def quality_check(self, passed: int, failed: int, context: Optional[dict] = None):
        """Log quality check results"""
        total = passed + failed
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        self.info(f"Quality Check Results:", {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{pass_rate:.1f}%"
        })
    
    def generation_error(self, topic: str, error: Exception, context: Optional[dict] = None):
        """Log generation error with context"""
        error_context = {
            "topic": topic,
            "error_type": type(error).__name__,
            "error_details": str(error)
        }
        if context:
            error_context.update(context)
        
        self.error(f"Generation error for topic '{topic}'", error_context)
    
    def batch_complete(self, batch_number: int, successful: int, failed: int):
        """Log batch completion statistics"""
        self.info(f"Batch {batch_number} complete", {
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / (successful + failed)) * 100:.1f}%"
        })

# Create global logger instance
logger = Logger()
