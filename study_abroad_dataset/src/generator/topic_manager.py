"""
Topic management module for balanced dataset generation.
Handles topic selection, distribution, and dynamic balancing.
"""

import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import numpy as np
from ..utils.config import Config
from ..utils.logger import logger

class TopicManager:
    """
    Manages topic selection and distribution to ensure balanced dataset generation
    across all topics and subtopics.
    """
    
    def __init__(self):
        self.config = Config
        self.topics = self.config.TOPICS
        self.topic_counts = defaultdict(int)
        self.subtopic_counts = defaultdict(lambda: defaultdict(int))
        self.topic_history = []  # Track recent topic selections
        
    def select_next_topic(self, target_distribution: Optional[Dict[str, int]] = None) -> Tuple[str, Dict]:
        """
        Select the next topic based on current distribution and target counts.
        Uses weighted random selection favoring underrepresented topics.
        """
        if not target_distribution:
            target_distribution = {
                topic: config["min_count"] 
                for topic, config in self.topics.items()
            }
        
        # Calculate topic weights based on current vs target distribution
        weights = self._calculate_topic_weights(target_distribution)
        
        # Adjust weights based on recent history to avoid repetition
        weights = self._adjust_weights_for_history(weights)
        
        # Select topic using weighted random choice
        total_weight = sum(weights.values())
        if total_weight == 0:
            logger.warning("All topics have reached their target counts")
            return random.choice(list(self.topics.keys())), self.topics[random.choice(list(self.topics.keys()))]
        
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for topic, weight in weights.items():
            cumulative_weight += weight
            if r <= cumulative_weight:
                # Update topic history
                self.topic_history.append(topic)
                if len(self.topic_history) > 5:  # Keep last 5 topics
                    self.topic_history.pop(0)
                
                return topic, self.topics[topic]
        
        # Fallback (shouldn't reach here)
        return list(self.topics.keys())[0], self.topics[list(self.topics.keys())[0]]
    
    def _calculate_topic_weights(self, target_distribution: Dict[str, int]) -> Dict[str, float]:
        """Calculate selection weights for each topic based on current distribution"""
        weights = {}
        
        for topic, config in self.topics.items():
            current_count = self.topic_counts[topic]
            target_count = target_distribution[topic]
            max_count = config["max_count"]
            
            if current_count >= max_count:
                weights[topic] = 0  # Topic has reached its maximum
                continue
            
            # Base weight from topic configuration
            base_weight = config["weight"]
            
            # Adjust weight based on progress towards target
            if current_count < target_count:
                # Increase weight for topics under target
                progress_ratio = current_count / target_count
                weights[topic] = base_weight * (2 - progress_ratio)
            else:
                # Decrease weight for topics over target
                overage_ratio = current_count / target_count
                weights[topic] = base_weight / overage_ratio
        
        return weights
    
    def _adjust_weights_for_history(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Adjust weights to avoid recent topic repetition"""
        adjusted_weights = weights.copy()
        
        # Reduce weights for recently used topics
        for i, topic in enumerate(reversed(self.topic_history)):
            if topic in adjusted_weights:
                # More recent topics get larger reduction
                reduction_factor = 0.5 ** (4 - i)  # 0.5, 0.25, 0.125, 0.0625
                adjusted_weights[topic] *= reduction_factor
        
        return adjusted_weights
    
    def select_subtopic(self, topic: str) -> str:
        """Select a subtopic ensuring balanced distribution within the topic"""
        subtopics = self.topics[topic]["subtopics"]
        
        # Calculate subtopic weights
        weights = {}
        total_subtopic_count = sum(self.subtopic_counts[topic].values())
        
        for subtopic in subtopics:
            current_count = self.subtopic_counts[topic][subtopic]
            if total_subtopic_count == 0:
                weights[subtopic] = 1  # Equal weights when starting fresh
            else:
                # Inverse weight based on current distribution
                distribution = current_count / total_subtopic_count
                weights[subtopic] = 1 - (distribution * 0.5)  # Soft balancing
        
        # Select subtopic using weighted random choice
        total_weight = sum(weights.values())
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for subtopic, weight in weights.items():
            cumulative_weight += weight
            if r <= cumulative_weight:
                return subtopic
        
        return subtopics[0]  # Fallback
    
    def record_generation(self, topic: str, subtopic: str):
        """Record successful generation for topic and subtopic"""
        self.topic_counts[topic] += 1
        self.subtopic_counts[topic][subtopic] += 1
        
        logger.debug(
            f"Recorded generation",
            {
                "topic": topic,
                "subtopic": subtopic,
                "topic_count": self.topic_counts[topic],
                "subtopic_count": self.subtopic_counts[topic][subtopic]
            }
        )
    
    def get_distribution_metrics(self) -> Dict:
        """Get current distribution metrics"""
        total_generations = sum(self.topic_counts.values())
        
        metrics = {
            "total_generations": total_generations,
            "topic_distribution": {},
            "subtopic_distribution": {},
            "balance_scores": {}
        }
        
        # Calculate topic distribution and balance
        for topic in self.topics:
            count = self.topic_counts[topic]
            if total_generations > 0:
                percentage = (count / total_generations) * 100
            else:
                percentage = 0
                
            metrics["topic_distribution"][topic] = {
                "count": count,
                "percentage": percentage
            }
            
            # Calculate subtopic balance score
            subtopic_counts = [
                self.subtopic_counts[topic][st] 
                for st in self.topics[topic]["subtopics"]
            ]
            
            if sum(subtopic_counts) > 0:
                # Use coefficient of variation as balance score
                mean = np.mean(subtopic_counts)
                std = np.std(subtopic_counts)
                cv = std / mean if mean > 0 else 0
                balance_score = 1 - min(cv, 1)  # Convert to 0-1 score where 1 is perfectly balanced
            else:
                balance_score = 1  # No generations yet
                
            metrics["balance_scores"][topic] = balance_score
            
            # Record subtopic distribution
            metrics["subtopic_distribution"][topic] = {
                subtopic: self.subtopic_counts[topic][subtopic]
                for subtopic in self.topics[topic]["subtopics"]
            }
        
        return metrics
    
    def is_balanced(self, threshold: float = 0.8) -> bool:
        """Check if current distribution is balanced within threshold"""
        metrics = self.get_distribution_metrics()
        
        # Check topic distribution
        if not metrics["topic_distribution"]:
            return False
            
        # Calculate maximum deviation from ideal distribution
        n_topics = len(self.topics)
        ideal_percentage = 100 / n_topics
        max_deviation = max(
            abs(data["percentage"] - ideal_percentage)
            for data in metrics["topic_distribution"].values()
        )
        
        # Check overall topic balance
        if max_deviation > (100 * (1 - threshold)):
            return False
            
        # Check subtopic balance scores
        if any(score < threshold for score in metrics["balance_scores"].values()):
            return False
            
        return True
    
    def get_underrepresented_topics(self, target_distribution: Dict[str, int]) -> List[str]:
        """Get list of topics that are under their target count"""
        return [
            topic for topic, target in target_distribution.items()
            if self.topic_counts[topic] < target
        ]
    
    def get_overrepresented_topics(self, target_distribution: Dict[str, int]) -> List[str]:
        """Get list of topics that are over their target count"""
        return [
            topic for topic, target in target_distribution.items()
            if self.topic_counts[topic] > target
        ]
