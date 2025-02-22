"""
Study Abroad Dataset Cleaner

A comprehensive tool for cleaning, validating, and balancing conversational datasets.

Features:
- Advanced duplicate detection using TF-IDF and cosine similarity
- Quality validation with multiple metrics (structure, content, relevance)
- Topic classification and balanced distribution
- Detailed logging and progress reporting
- Configurable parameters for fine-tuning

Example usage:
    python clean_dataset.py --input dataset/raw.jsonl --output dataset/cleaned.jsonl --target-size 5000
"""

import json
import datetime
import logging
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from tqdm import tqdm
import traceback
from collections import Counter, defaultdict
import random
import copy
import sys
import argparse
import statistics
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dataset_cleaner.log')
    ]
)
logger = logging.getLogger(__name__)

class DatasetCleaner:
    def __init__(self):
        logger.info("Initializing DatasetCleaner...")
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        self.quality_indicators = [
            "this is important because",
            "for example",
            "such as",
            "this means",
            "because",
            "therefore",
            "furthermore",
            "importantly",
            "specifically",
            "notably"
        ]
        self.topics = {
            "admission": [
                "admission", "requirements", "application", "sop", "test scores",
                "gre", "gmat", "ielts", "toefl", "transcript", "recommendation letter",
                "documents", "deadline", "criteria", "eligibility"
            ],
            "scholarships": [
                "scholarship", "financial aid", "funding", "grant", "fellowship",
                "stipend", "tuition fee", "waiver", "assistantship", "merit-based",
                "need-based", "full funding", "partial funding"
            ],
            "visa": [
                "visa", "immigration", "permit", "passport", "embassy", "consulate",
                "student visa", "dependent visa", "work permit", "visa interview",
                "i20", "sevis", "documentation"
            ],
            "housing": [
                "housing", "accommodation", "dorm", "apartment", "rent", "dormitory",
                "residence hall", "off-campus", "on-campus", "lease", "utilities",
                "roommate", "shared housing"
            ],
            "cost": [
                "cost", "expense", "budget", "fee", "living cost", "tuition",
                "monthly expenses", "food cost", "living expenses", "estimated cost",
                "financial planning", "cost of living"
            ],
            "culture": [
                "culture", "adapt", "lifestyle", "tradition", "customs",
                "cultural shock", "social life", "integration", "diversity",
                "local culture", "international student", "adjustment"
            ],
            "healthcare": [
                "health", "insurance", "medical", "hospital", "clinic",
                "healthcare system", "mental health", "wellness", "emergency",
                "doctor", "vaccination", "coverage"
            ],
            "language": [
                "language", "english", "proficiency", "ielts", "toefl",
                "language requirement", "language course", "esl", "language support",
                "language center", "language preparation"
            ],
            "transportation": [
                "transport", "commute", "bus", "train", "bicycle", "subway",
                "public transit", "transportation system", "campus shuttle",
                "parking", "car", "walking distance"
            ],
            "job": [
                "job", "career", "internship", "work", "employment", "opt",
                "cpt", "part-time work", "job market", "career services",
                "placement", "job search", "work permit"
            ],
            "research": [
                "research", "thesis", "laboratory", "professor", "publication",
                "research project", "research funding", "research assistant",
                "supervisor", "research topics", "lab work"
            ],
            "university": [
                "university", "college", "campus", "institution", "department",
                "faculty", "school", "academic", "ranking", "reputation",
                "facilities", "resources", "library"
            ],
            "student_life": [
                "student life", "activities", "club", "sports", "events",
                "student organization", "campus life", "recreation", "gym",
                "student union", "social activities", "extracurricular"
            ]
        }
        logger.info("DatasetCleaner initialized successfully")

    def load_dataset(self, filepath: str) -> List[Dict]:
        """Load dataset from JSONL file"""
        try:
            conversations = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    conversations.append(json.loads(line.strip()))
            logger.info(f"Successfully loaded {len(conversations)} conversations from {filepath}")
            return conversations
        except Exception as e:
            logger.error(f"Error loading dataset from {filepath}: {str(e)}")
            raise

    def save_dataset(self, conversations: List[Dict], filepath: str):
        """Save dataset to JSONL file"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                for conv in conversations:
                    f.write(json.dumps(conv, ensure_ascii=False) + '\n')
            logger.info(f"Successfully saved {len(conversations)} conversations to {filepath}")
        except Exception as e:
            logger.error(f"Error saving dataset to {filepath}: {str(e)}")
            raise

    def get_conversation_text(self, conversation: Dict) -> str:
        """Extract all assistant responses from a conversation"""
        return ' '.join([
            turn['value'] for turn in conversation['conversations']
            if turn['from'] == 'assistant'
        ])

    def check_quality(self, conversation: Dict) -> bool:
        """Check conversation quality based on key criteria"""
        text = ' '.join([
            turn['value'].lower() for turn in conversation['conversations']
            if turn['from'] == 'assistant'
        ])
        
        # Length check
        if len(text.split()) < 120:
            return False
        
        # Quality indicators check
        quality_count = sum(1 for phrase in self.quality_indicators if phrase in text)
        if quality_count < 1:
            return False
        
        # Format check
        if '##' not in text or '*' not in text:
            return False
        
        # Structure check (lists)
        if not bool(re.search(r'(\n[*-]|\n\d+\.)\s', text)):
            return False
        
        return True

    def get_topic_scores(self, text: str) -> Dict[str, float]:
        """Calculate topic relevance scores"""
        text = text.lower()
        scores = {}
        words = text.split()
        word_freq = Counter(words)
        
        for topic, keywords in self.topics.items():
            score = 0
            for keyword in keywords:
                # Multi-word keywords get higher weight
                if ' ' in keyword:
                    if keyword in text:
                        score += 3
                else:
                    score += word_freq.get(keyword, 0)
            scores[topic] = score
        
        return scores

    def get_top_topics(self, text: str, threshold: float = 0.3, max_topics: int = 2) -> List[str]:
        """Get main topics of a conversation"""
        scores = self.get_topic_scores(text)
        max_score = max(scores.values()) if scores else 1
        
        # Normalize scores
        norm_scores = {k: v/max_score for k, v in scores.items()}
        
        # Get topics above threshold, sorted by score
        topics = [(topic, score) for topic, score in norm_scores.items() if score >= threshold]
        topics.sort(key=lambda x: x[1], reverse=True)
        
        return [topic for topic, _ in topics[:max_topics]]

    def find_duplicates(self, texts: List[str], threshold: float = 0.85) -> set:
        """Find duplicate texts using batched processing"""
        duplicates = set()
        batch_size = 100
        n = len(texts)
        
        logger.info("Computing TF-IDF vectors...")
        vectors = self.vectorizer.fit_transform(texts)
        
        logger.info("Finding duplicates in batches...")
        for i in tqdm(range(0, n, batch_size)):
            batch_end = min(i + batch_size, n)
            batch_vectors = vectors[i:batch_end]
            
            if batch_end < n:
                similarities = cosine_similarity(batch_vectors, vectors[batch_end:])
                
                duplicate_mask = similarities > threshold
                for row_idx, row in enumerate(duplicate_mask):
                    duplicate_cols = np.where(row)[0]
                    if len(duplicate_cols) > 0:
                        orig_idx = i + row_idx
                        for col_idx in duplicate_cols:
                            dup_idx = batch_end + col_idx
                            if len(texts[orig_idx]) >= len(texts[dup_idx]):
                                duplicates.add(dup_idx)
                            else:
                                duplicates.add(orig_idx)
                                break
        
        logger.info(f"Found {len(duplicates)} duplicate conversations")
        return duplicates

    def upsample_conversation(self, conv: Dict) -> Dict:
        """Create a variation of a conversation"""
        new_conv = copy.deepcopy(conv)
        
        for turn in new_conv['conversations']:
            if turn['from'] == 'assistant':
                sections = turn['value'].split('##')
                new_sections = []
                
                for section in sections:
                    if not section.strip():
                        continue
                    
                    lines = section.split('\n')
                    heading = lines[0]
                    content = '\n'.join(lines[1:])
                    
                    # Modify content while preserving structure
                    words = content.split()
                    for i in range(len(words)):
                        if random.random() < 0.1:  # 10% chance to modify
                            modifiers = ['additionally', 'importantly', 'notably', 'specifically']
                            words[i] = random.choice(modifiers) + ' ' + words[i]
                    
                    new_content = ' '.join(words)
                    new_sections.append(f"## {heading}\n{new_content}")
                
                turn['value'] = '\n\n'.join(new_sections)
        
        return new_conv

    def balance_dataset(self, conversations: List[Dict], target_per_topic: int) -> List[Dict]:
        """Balance dataset with strict topic distribution control"""
        # Set hard limits per topic
        MIN_PER_TOPIC = min(target_per_topic // 2, 300)  # Minimum 300 per topic
        MAX_PER_TOPIC = min(target_per_topic, 500)       # Maximum 500 per topic
        
        # Initialize tracking
        topic_groups = {topic: [] for topic in self.topics.keys()}
        conv_topics = {}
        balanced = []
        seen = set()
        
        logger.info("\nStep 1: Initial topic analysis...")
        # First pass: Group conversations by topics
        for conv in tqdm(conversations, desc="Analyzing topics"):
            text = self.get_conversation_text(conv)
            primary_topics = self.get_top_topics(text, threshold=0.3, max_topics=1)
            secondary_topics = self.get_top_topics(text, threshold=0.2, max_topics=2)
            all_topics = list(set(primary_topics + secondary_topics))
            conv_topics[text] = all_topics
            
            if primary_topics:
                topic_groups[primary_topics[0]].append(conv)
        
        logger.info("\nInitial topic distribution:")
        for topic, group in topic_groups.items():
            logger.info(f"- {topic}: {len(group)} conversations")
        
        # Second pass: Add high-quality conversations within limits
        logger.info("\nStep 2: Adding core conversations...")
        topic_counts = {topic: 0 for topic in self.topics.keys()}
        
        for topic, group in topic_groups.items():
            group.sort(key=lambda x: len(self.get_conversation_text(x)), reverse=True)
            
            for conv in group:
                text = self.get_conversation_text(conv)
                if text not in seen and topic_counts[topic] < MAX_PER_TOPIC:
                    balanced.append(conv)
                    seen.add(text)
                    topic_counts[topic] += 1
        
        # Third pass: Upsample underrepresented topics
        logger.info("\nStep 3: Balancing underrepresented topics...")
        for topic in self.topics.keys():
            current = topic_counts[topic]
            if current < MIN_PER_TOPIC:
                needed = MIN_PER_TOPIC - current
                logger.info(f"- {topic}: needs {needed} more conversations")
                
                base_convs = [conv for conv in topic_groups[topic] 
                             if self.get_conversation_text(conv) not in seen]
                
                if base_convs:
                    base_convs.sort(key=lambda x: len(self.get_conversation_text(x)), reverse=True)
                    base_convs = base_convs[:5]  # Use top 5 as templates
                    
                    while needed > 0 and base_convs:
                        base_conv = random.choice(base_convs)
                        new_conv = self.upsample_conversation(base_conv)
                        new_text = self.get_conversation_text(new_conv)
                        
                        if new_text not in seen:
                            balanced.append(new_conv)
                            seen.add(new_text)
                            needed -= 1
                            topic_counts[topic] += 1
        
        logger.info("\nFinal topic distribution:")
        for topic, count in sorted(topic_counts.items()):
            logger.info(f"- {topic}: {count} conversations")
        
        return balanced

    def clean_dataset(self, input_file: str, output_file: str, target_size: int = 5000):
        """Clean and balance the dataset"""
        try:
            logger.info("="*50)
            logger.info("Starting Dataset Cleaning Process")
            logger.info("="*50)
            
            logger.info("\nStep 1: Loading dataset...")
            conversations = self.load_dataset(input_file)
            original_count = len(conversations)
            logger.info(f"Loaded {original_count} conversations")
            
            # Step 2: Quality check
            logger.info("\nStep 2: Performing quality checks...")
            quality_passed = []
            quality_metrics = defaultdict(int)
            
            for conv in tqdm(conversations, desc="Checking quality"):
                if self.check_quality(conv):
                    quality_passed.append(conv)
                    quality_metrics['passed'] += 1
                else:
                    quality_metrics['failed'] += 1
            
            logger.info(f"Quality check results:")
            logger.info(f"- Passed: {quality_metrics['passed']} conversations")
            logger.info(f"- Failed: {quality_metrics['failed']} conversations")
            
            # Step 3: Remove duplicates
            logger.info("\nStep 3: Removing duplicates...")
            texts = [self.get_conversation_text(conv) for conv in quality_passed]
            duplicate_indices = self.find_duplicates(texts)
            
            unique_conversations = [
                conv for idx, conv in enumerate(quality_passed)
                if idx not in duplicate_indices
            ]
            
            logger.info(f"Removed {len(duplicate_indices)} duplicate conversations")
            logger.info(f"Remaining: {len(unique_conversations)} conversations")
            
            # Step 4: Balance dataset
            logger.info("\nStep 4: Balancing dataset...")
            target_per_topic = max(50, target_size // len(self.topics))
            balanced_conversations = self.balance_dataset(
                unique_conversations, target_per_topic
            )
            
            # Step 5: Final quality check and save
            logger.info("\nStep 5: Saving cleaned dataset...")
            self.save_dataset(balanced_conversations, output_file)
            
            # Generate report
            logger.info("\nCleaning Process Complete!")
            logger.info("="*50)
            logger.info("Summary:")
            logger.info(f"- Original conversations: {original_count}")
            logger.info(f"- After quality check: {len(quality_passed)}")
            logger.info(f"- After deduplication: {len(unique_conversations)}")
            logger.info(f"- Final balanced dataset: {len(balanced_conversations)}")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"Error during dataset cleaning: {str(e)}")
            logger.error(traceback.format_exc())
            raise

def main():
    """CLI interface for dataset cleaning"""
    parser = argparse.ArgumentParser(
        description="Clean and balance a study abroad Q&A dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input JSONL file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output JSONL file'
    )
    parser.add_argument(
        '--target-size',
        type=int,
        default=5000,
        help='Target number of conversations (default: 5000)'
    )
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.85,
        help='Threshold for duplicate detection (0.0-1.0, default: 0.85)'
    )
    
    args = parser.parse_args()
    
    try:
        cleaner = DatasetCleaner()
        cleaner.clean_dataset(
            input_file=args.input,
            output_file=args.output,
            target_size=args.target_size
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
