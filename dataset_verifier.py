import os
import json
import hashlib
from typing import List, Dict, Set
from collections import defaultdict
from datetime import datetime

class DatasetVerifier:
    def __init__(self, dataset_path: str = "dataset/study_abroad_dataset.jsonl"):
        self.dataset_path = dataset_path
        self.hashes: Set[str] = set()
        self.duplicates: List[Dict] = []
        self._load_existing_hashes()
        
    def _load_existing_hashes(self):
        """Load hashes of existing conversations"""
        if not os.path.exists(self.dataset_path):
            return
            
        with open(self.dataset_path, 'r') as f:
            for line in f:
                try:
                    conversation = json.loads(line)
                    conv_hash = self.compute_conversation_hash(conversation)
                    self.hashes.add(conv_hash)
                except json.JSONDecodeError:
                    continue
        
    def compute_conversation_hash(self, conversation: Dict) -> str:
        """Compute a hash of conversation content to detect duplicates"""
        # Convert conversation to a consistent string format
        conv_str = json.dumps(conversation, sort_keys=True)
        return hashlib.sha256(conv_str.encode()).hexdigest()
    
    def is_duplicate(self, conversation: Dict) -> bool:
        """Check if a conversation is a duplicate"""
        conv_hash = self.compute_conversation_hash(conversation)
        if conv_hash in self.hashes:
            return True
        self.hashes.add(conv_hash)
        return False
        
    def check_duplicates(self) -> List[Dict]:
        """Find duplicate conversations in the dataset"""
        print(f"\nChecking for duplicates in: {self.dataset_path}")
        
        if not os.path.exists(self.dataset_path):
            print("Dataset file not found!")
            return []
            
        seen_hashes = {}
        duplicates = []
        total_conversations = 0
        
        with open(self.dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    conversation = json.loads(line)
                    total_conversations += 1
                    
                    # Compute hash
                    conv_hash = self.compute_conversation_hash(conversation)
                    
                    # Check for duplicate
                    if conv_hash in seen_hashes:
                        duplicates.append({
                            "line_number": line_num,
                            "duplicate_of": seen_hashes[conv_hash],
                            "conversation": conversation
                        })
                    else:
                        seen_hashes[conv_hash] = line_num
                        
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON at line {line_num}")
                    continue
                    
        print(f"\nAnalysis complete:")
        print(f"- Total conversations: {total_conversations}")
        print(f"- Unique conversations: {len(seen_hashes)}")
        print(f"- Duplicates found: {len(duplicates)}")
        
        return duplicates
        
    def remove_duplicates(self) -> None:
        """Remove duplicate conversations from the dataset"""
        duplicates = self.check_duplicates()
        
        if not duplicates:
            print("No duplicates found!")
            return
            
        # Create backup
        backup_path = f"{self.dataset_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(self.dataset_path, backup_path)
        print(f"\nCreated backup: {backup_path}")
        
        # Write deduplicated dataset
        duplicate_lines = set(d["line_number"] for d in duplicates)
        written = 0
        
        with open(backup_path, 'r') as src, open(self.dataset_path, 'w') as dst:
            for line_num, line in enumerate(src, 1):
                if line_num not in duplicate_lines:
                    dst.write(line)
                    written += 1
                    
        print(f"\nDuplicates removed:")
        print(f"- Original conversations: {written + len(duplicates)}")
        print(f"- Duplicates removed: {len(duplicates)}")
        print(f"- Remaining conversations: {written}")
        
    def check_status(self) -> Dict:
        """Check dataset generation status and progress"""
        status = {
            "total_conversations": 0,
            "topics": defaultdict(int),
            "file_size": 0,
            "last_modified": None
        }
        
        if not os.path.exists(self.dataset_path):
            return status
            
        status["file_size"] = os.path.getsize(self.dataset_path)
        status["last_modified"] = datetime.fromtimestamp(
            os.path.getmtime(self.dataset_path)
        ).strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.dataset_path, 'r') as f:
            for line in f:
                try:
                    conversation = json.loads(line)
                    status["total_conversations"] += 1
                    
                    # Identify topic from first question
                    if conversation["conversations"]:
                        first_q = conversation["conversations"][0]["value"].lower()
                        for topic in ["visa", "scholarship", "university", "admission", "job"]:
                            if topic in first_q:
                                status["topics"][f"{topic}_related"] += 1
                                break
                                
                except json.JSONDecodeError:
                    continue
                    
        return status
