import os
import json
import time
import traceback
from tqdm.auto import tqdm
from typing import List, Dict, Optional
from main import StudyAbroadDataGenerator
from dataset_verifier import DatasetVerifier

class ResumableDatasetGenerator:
    def __init__(self, output_dir: str = "dataset", batch_size: int = 3):  # Reduced batch size
        self.generator = StudyAbroadDataGenerator()
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.progress_file = os.path.join(output_dir, "generation_progress.json")
        self.conversations_file = os.path.join(output_dir, "study_abroad_dataset.jsonl")
        self.verifier = DatasetVerifier(self.conversations_file)
        os.makedirs(output_dir, exist_ok=True)
        
    def load_progress(self) -> Dict:
        """Load generation progress from file"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "total_generated": 0,
            "topics_progress": {topic: 0 for topic in self.generator.config["TOPICS"].keys()},
            "failed_attempts": []
        }
        
    def save_progress(self, progress: Dict):
        """Save generation progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
            
    def append_conversations(self, conversations: List[Dict]):
        """Append new conversations to the dataset file"""
        mode = 'a' if os.path.exists(self.conversations_file) else 'w'
        with open(self.conversations_file, mode, encoding='utf-8') as f:
            for conv in conversations:
                f.write(json.dumps(conv, ensure_ascii=False) + "\n")
                
    def log_error(self, topic: str, error: Exception):
        """Log generation errors for debugging"""
        error_file = os.path.join(self.output_dir, "generation_errors.log")
        with open(error_file, 'a') as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error generating {topic}:\n")
            f.write(traceback.format_exc())
            f.write("\n" + "="*80 + "\n")

    def generate_dataset(self, total_conversations: int = 200, max_retries: int = 5) -> None:  # Increased max retries
        """Generate full dataset with progress tracking and error handling"""
        progress = self.load_progress()
        remaining = total_conversations - progress["total_generated"]
        
        if remaining <= 0:
            print(f"Dataset already complete with {progress['total_generated']} conversations")
            return
            
        print(f"\nResuming dataset generation from {progress['total_generated']} conversations")
        print(f"Generating {remaining} more conversations...")
        
        topics = list(self.generator.config["TOPICS"].keys())
        conversations_per_topic = max(1, remaining // len(topics))
        
        with tqdm(total=remaining) as pbar:
            for topic in topics:
                topic_progress = progress["topics_progress"].get(topic, 0)
                target = conversations_per_topic
                
                while topic_progress < target:
                    batch_conversations = []
                    batch_size = min(self.batch_size, target - topic_progress)
                    retries = 0
                    
                    while len(batch_conversations) < batch_size and retries < max_retries:
                        try:
                            conversation = self.generator.generate_conversation(topic)
                            if conversation and len(conversation["conversations"]) >= 4:
                                # Check for duplicates before adding
                                if not self.verifier.is_duplicate(conversation):
                                    batch_conversations.append(conversation)
                                    topic_progress += 1
                                    progress["total_generated"] += 1
                                    pbar.update(1)
                                else:
                                    print(f"\nSkipping duplicate conversation for topic: {topic}")
                                    retries += 1
                            else:
                                retries += 1
                                
                        except Exception as e:
                            self.log_error(topic, e)
                            retries += 1
                        
                        # Save progress after each successful conversation
                        if batch_conversations:
                            progress["topics_progress"][topic] = topic_progress
                            self.save_progress(progress)
                            self.append_conversations(batch_conversations)
                        
                        time.sleep(5)  # Increased delay for rate limiting
                    
                    if retries >= max_retries:
                        print(f"\nWarning: Max retries reached for topic {topic}")
                        progress["failed_attempts"].append({
                            "topic": topic,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "remaining": target - topic_progress
                        })
                        self.save_progress(progress)
                        break
        
        print("\nDataset generation complete!")
        print(f"Total conversations generated: {progress['total_generated']}")
        print(f"Dataset saved to: {self.conversations_file}")
        
        if progress["failed_attempts"]:
            print("\nWarning: Some generation attempts failed:")
            for failure in progress["failed_attempts"]:
                print(f"- Topic: {failure['topic']}, Remaining: {failure['remaining']}")
            print("Check generation_errors.log for details")

def main():
    try:
        # Configure the generator
        generator = ResumableDatasetGenerator(
            output_dir="dataset",
            batch_size=3  # Process in smaller batches
        )
        
        # Generate dataset with reduced target
        generator.generate_dataset(total_conversations=10000)
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
