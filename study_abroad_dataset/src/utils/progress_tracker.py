"""
Progress tracking module for dataset generation.
Handles checkpointing, progress persistence, and recovery from interruptions.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .logger import logger
from .config import Config

class ProgressTracker:
    """
    Tracks and manages dataset generation progress, providing
    checkpoint functionality and progress persistence.
    """
    
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        self.progress_file = self.output_dir / "generation_progress.json"
        self.checkpoint_dir = self.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Initialize progress data
        self.progress_data = self._load_progress()
        
        # Track batch metrics
        self.current_batch = {
            "number": 0,
            "successful": 0,
            "failed": 0,
            "start_time": None
        }
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load progress from file or initialize new progress tracking"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                logger.info("Loaded existing progress data")
                return data
            except json.JSONDecodeError:
                logger.warning("Corrupted progress file, starting fresh")
        
        # Initialize new progress tracking
        return {
            "start_time": datetime.now().isoformat(),
            "total_generated": 0,
            "total_failed": 0,
            "topic_progress": {topic: 0 for topic in Config.TOPICS.keys()},
            "quality_metrics": {
                "passed": 0,
                "failed": 0
            },
            "checkpoints": [],
            "last_save": datetime.now().isoformat()
        }
    
    def save_progress(self):
        """Save current progress to file"""
        try:
            self.progress_data["last_save"] = datetime.now().isoformat()
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
            logger.debug("Progress saved successfully")
        except Exception as e:
            logger.error(f"Failed to save progress: {str(e)}")
    
    def create_checkpoint(self):
        """Create a checkpoint of current progress"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.checkpoint_dir / f"checkpoint_{timestamp}.json"
            
            checkpoint_data = {
                "timestamp": timestamp,
                "progress": self.progress_data.copy(),
                "batch_state": self.current_batch.copy()
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Update checkpoints list
            self.progress_data["checkpoints"].append(timestamp)
            self.save_progress()
            
            logger.info(f"Created checkpoint: {checkpoint_file.name}")
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {str(e)}")
    
    def restore_checkpoint(self, timestamp: Optional[str] = None) -> bool:
        """
        Restore progress from a checkpoint.
        If no timestamp provided, uses the latest checkpoint.
        """
        try:
            if not timestamp:
                if not self.progress_data["checkpoints"]:
                    logger.warning("No checkpoints available")
                    return False
                timestamp = self.progress_data["checkpoints"][-1]
            
            checkpoint_file = self.checkpoint_dir / f"checkpoint_{timestamp}.json"
            if not checkpoint_file.exists():
                logger.error(f"Checkpoint file not found: {checkpoint_file}")
                return False
            
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            self.progress_data = checkpoint_data["progress"]
            self.current_batch = checkpoint_data["batch_state"]
            self.save_progress()
            
            logger.info(f"Restored from checkpoint: {timestamp}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {str(e)}")
            return False
    
    def start_batch(self, batch_number: int):
        """Start tracking a new batch"""
        self.current_batch = {
            "number": batch_number,
            "successful": 0,
            "failed": 0,
            "start_time": time.time()
        }
        logger.debug(f"Started batch {batch_number}")
    
    def record_success(self, topic: str):
        """Record a successful conversation generation"""
        self.progress_data["total_generated"] += 1
        self.progress_data["topic_progress"][topic] += 1
        self.current_batch["successful"] += 1
        
        # Create checkpoint if needed
        if (self.progress_data["total_generated"] % 
            Config.PROGRESS["checkpoint_interval"] == 0):
            self.create_checkpoint()
        
        # Save progress if needed
        if (self.progress_data["total_generated"] % 
            Config.PROGRESS["save_interval"] == 0):
            self.save_progress()
    
    def record_failure(self, topic: str):
        """Record a failed conversation generation"""
        self.progress_data["total_failed"] += 1
        self.current_batch["failed"] += 1
        self.save_progress()
    
    def record_quality_check(self, passed: bool):
        """Record quality check result"""
        if passed:
            self.progress_data["quality_metrics"]["passed"] += 1
        else:
            self.progress_data["quality_metrics"]["failed"] += 1
    
    def end_batch(self) -> Dict[str, Any]:
        """End current batch and return metrics"""
        duration = time.time() - self.current_batch["start_time"]
        metrics = {
            "batch_number": self.current_batch["number"],
            "successful": self.current_batch["successful"],
            "failed": self.current_batch["failed"],
            "duration": duration,
            "success_rate": (self.current_batch["successful"] / 
                           (self.current_batch["successful"] + 
                            self.current_batch["failed"]) * 100
                           if self.current_batch["successful"] + 
                              self.current_batch["failed"] > 0 else 0)
        }
        
        logger.batch_complete(
            self.current_batch["number"],
            self.current_batch["successful"],
            self.current_batch["failed"]
        )
        
        return metrics
    
    def get_topic_distribution(self) -> Dict[str, int]:
        """Get current topic distribution"""
        return self.progress_data["topic_progress"].copy()
    
    def get_quality_metrics(self) -> Dict[str, int]:
        """Get current quality metrics"""
        return self.progress_data["quality_metrics"].copy()
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get overall generation summary"""
        return {
            "total_generated": self.progress_data["total_generated"],
            "total_failed": self.progress_data["total_failed"],
            "topic_distribution": self.get_topic_distribution(),
            "quality_metrics": self.get_quality_metrics(),
            "start_time": self.progress_data["start_time"],
            "last_save": self.progress_data["last_save"],
            "checkpoints": len(self.progress_data["checkpoints"])
        }
