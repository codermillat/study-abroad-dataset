"""
Main script for generating the study abroad Q&A dataset.
Orchestrates the entire generation process with proper error handling and monitoring.
"""

import os
import json
import argparse
from pathlib import Path
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Add the src directory to Python path
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from src.utils.config import Config
from src.utils.logger import logger
from src.utils.progress_tracker import ProgressTracker
from src.generator.conversation_generator import ConversationGenerator, InvalidAPIKeyError

def check_api_key() -> bool:
    """Check if API key is properly configured"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not found")
        logger.info("Please set your API key in the .env file:")
        logger.info("GEMINI_API_KEY=your_key_here")
        return False
    
    if not api_key.startswith('AI') or len(api_key) < 20:
        logger.error("API key appears to be invalid")
        logger.info("Please get a valid API key from https://makersuite.google.com/app/apikey")
        return False
    
    return True

class DatasetGenerationOrchestrator:
    """
    Orchestrates the dataset generation process with proper monitoring,
    error handling, and progress tracking.
    """
    
    def __init__(self, args: dict):
        self.config = Config
        self.progress_tracker = ProgressTracker()
        
        # Configuration
        self.total_conversations = args["total_conversations"]
        self.batch_size = args.get("batch_size", Config.BATCH_SIZE)
        self.output_dir = Path(args.get("output_dir", Config.OUTPUT_DIR))
        self.output_file = self.output_dir / "study_abroad_dataset.jsonl"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self.generator = ConversationGenerator()
        except InvalidAPIKeyError as e:
            logger.error(str(e))
            raise
    
    def generate_batch(self, batch_number: int) -> None:
        """Generate a batch of conversations"""
        self.progress_tracker.start_batch(batch_number)
        
        # Generate conversations in parallel using threads
        with ThreadPoolExecutor(max_workers=self.batch_size) as executor:
            completed = list(executor.map(
                lambda _: self.generator.generate_conversation(),
                range(self.batch_size)
            ))
        
        # Filter out failed generations and save successful ones
        successful = [conv for conv in completed if conv is not None]
        
        if successful:
            self._save_conversations(successful)
            
        # Update progress
        metrics = self.progress_tracker.end_batch()
        logger.info(f"Batch {batch_number} complete", metrics)
    
    def _save_conversations(self, conversations: list) -> None:
        """Save conversations to output file"""
        try:
            mode = 'a' if self.output_file.exists() else 'w'
            with open(self.output_file, mode, encoding='utf-8') as f:
                for conv in conversations:
                    f.write(f"{json.dumps(conv, ensure_ascii=False)}\n")
        except Exception as e:
            logger.error(f"Error saving conversations: {str(e)}")
            raise
    
    def _should_continue(self) -> bool:
        """Check if generation should continue"""
        metrics = self.progress_tracker.get_generation_summary()
        return metrics["total_generated"] < self.total_conversations
    
    def generate_dataset(self) -> None:
        """
        Generate the complete dataset with proper monitoring
        and error handling.
        """
        try:
            logger.info("Starting dataset generation", {
                "total_target": self.total_conversations,
                "batch_size": self.batch_size
            })
            
            batch_number = 0
            
            while self._should_continue():
                batch_number += 1
                
                try:
                    self.generate_batch(batch_number)
                    
                    # Log progress
                    metrics = self.progress_tracker.get_generation_summary()
                    if metrics["total_generated"] > 0:
                        success_rate = (
                            metrics["total_generated"] / 
                            (metrics["total_generated"] + metrics["total_failed"])
                            * 100
                        )
                    else:
                        success_rate = 0
                        
                    logger.info("Generation progress", {
                        "completed": metrics["total_generated"],
                        "remaining": self.total_conversations - metrics["total_generated"],
                        "success_rate": f"{success_rate:.1f}%"
                    })
                    
                except Exception as e:
                    logger.error(f"Error in batch {batch_number}: {str(e)}")
                    if "API_KEY_INVALID" in str(e):
                        logger.error("Invalid API key detected. Stopping generation.")
                        break
                    continue
            
            # Final report
            final_metrics = self.progress_tracker.get_generation_summary()
            logger.info("Dataset generation complete!", final_metrics)
            
        except Exception as e:
            logger.critical(f"Critical error in dataset generation: {str(e)}")
            raise

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Generate a high-quality study abroad Q&A dataset"
    )
    
    parser.add_argument(
        "--total-conversations",
        type=int,
        default=5000,
        help="Total number of conversations to generate"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=Config.BATCH_SIZE,
        help="Number of conversations to generate in parallel"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Config.OUTPUT_DIR),
        help="Directory to save the generated dataset"
    )
    
    args = parser.parse_args()
    
    # Check API key before proceeding
    if not check_api_key():
        sys.exit(1)
    
    # Validate configuration
    if not Config.validate_config():
        logger.critical("Invalid configuration")
        return
    
    try:
        # Create and run orchestrator
        orchestrator = DatasetGenerationOrchestrator(vars(args))
        orchestrator.generate_dataset()
    except InvalidAPIKeyError:
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Generation interrupted by user")
    except Exception as e:
        logger.critical(f"Unhandled error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
