import json
from collections import defaultdict
import re
from typing import List, Dict, Any

class DatasetEvaluator:
    def __init__(self):
        self.format_issues = []
        self.content_issues = []
        self.metrics = defaultdict(list)
        
    def check_format_consistency(self, conversation: List[Dict[str, str]]) -> bool:
        """Verify ChatML format consistency"""
        if not conversation:
            self.format_issues.append("Empty conversation")
            return False
            
        for turn in conversation:
            if not isinstance(turn, dict):
                self.format_issues.append(f"Invalid turn format: {turn}")
                return False
            if 'from' not in turn or 'value' not in turn:
                self.format_issues.append(f"Missing required fields: {turn}")
                return False
            if turn['from'] not in ['human', 'assistant']:
                self.format_issues.append(f"Invalid role: {turn['from']}")
                return False
            if not isinstance(turn['value'], str) or not turn['value'].strip():
                self.format_issues.append(f"Invalid or empty message: {turn}")
                return False
        return True

    def evaluate_information_quality(self, response: str) -> Dict[str, Any]:
        """Analyze response for information quality and training signal"""
        metrics = {
            'has_facts': False,
            'has_reasoning': False,
            'has_examples': False,
            'has_structure': False,
            'readability': 0
        }
        
        # Check for factual content (dates, numbers, names, etc.)
        facts_pattern = r'\b\d+(?:\.\d+)?%?\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b|\b[A-Z][a-zA-Z]+ (?:University|College|Institute)\b'
        metrics['has_facts'] = bool(re.search(facts_pattern, response))
        
        # Check for reasoning patterns
        reasoning_patterns = ['because', 'therefore', 'as a result', 'this means', 'consequently', 'due to']
        metrics['has_reasoning'] = any(pattern in response.lower() for pattern in reasoning_patterns)
        
        # Check for examples
        example_patterns = ['for example', 'such as', 'like', 'instance', 'specifically']
        metrics['has_examples'] = any(pattern in response.lower() for pattern in example_patterns)
        
        # Check for structure
        structure_patterns = [r'\d\.|•|-|\*|First|Second|Finally|Moreover|Additionally']
        metrics['has_structure'] = any(re.search(pattern, response) for pattern in structure_patterns)
        
        # Basic readability score (0-100)
        words = response.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        sentences = len(re.split(r'[.!?]+', response))
        metrics['readability'] = min(100, max(0, 100 - (avg_word_length - 5) * 10 - (len(words)/sentences - 15) * 5))
        
        return metrics

    def check_conversation_coherence(self, conversation: List[Dict[str, str]]) -> Dict[str, float]:
        """Analyze conversation flow and context utilization"""
        coherence_metrics = {
            'context_usage': 0.0,
            'topic_consistency': 0.0,
            'turn_balance': 0.0
        }
        
        if len(conversation) < 4:  # Need at least 2 Q&A pairs
            return coherence_metrics
            
        # Analyze context usage in follow-up responses
        for i in range(3, len(conversation), 2):  # Start from second response
            prev_response = conversation[i-2]['value'].lower()
            curr_response = conversation[i]['value'].lower()
            
            # Check for context carryover
            prev_words = set(prev_response.split())
            curr_words = set(curr_response.split())
            context_overlap = len(prev_words.intersection(curr_words)) / len(prev_words)
            coherence_metrics['context_usage'] += context_overlap
            
        coherence_metrics['context_usage'] /= (len(conversation) // 2 - 1) if len(conversation) > 2 else 1
        
        # Check topic consistency
        first_question = conversation[0]['value'].lower()
        topic_words = set(first_question.split())
        topic_consistency = []
        
        for i in range(2, len(conversation), 2):  # Check follow-up questions
            follow_up = conversation[i]['value'].lower()
            follow_up_words = set(follow_up.split())
            overlap = len(topic_words.intersection(follow_up_words)) / len(topic_words)
            topic_consistency.append(overlap)
            
        coherence_metrics['topic_consistency'] = sum(topic_consistency) / len(topic_consistency) if topic_consistency else 0
        
        # Check turn balance (response length relative to question)
        turn_ratios = []
        for i in range(0, len(conversation), 2):
            if i+1 < len(conversation):
                question_len = len(conversation[i]['value'].split())
                response_len = len(conversation[i+1]['value'].split())
                ratio = min(1.0, max(0.0, (response_len - question_len) / question_len))
                turn_ratios.append(ratio)
                
        coherence_metrics['turn_balance'] = sum(turn_ratios) / len(turn_ratios) if turn_ratios else 0
        
        return coherence_metrics

    def evaluate_dataset(self, file_path: str):
        print("Evaluating dataset for fine-tuning suitability...\n")
        
        total_conversations = 0
        valid_format_count = 0
        total_turns = 0
        info_quality_scores = defaultdict(list)
        coherence_scores = defaultdict(list)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    conversation = data.get('conversations', [])
                    total_conversations += 1
                    
                    # Check format
                    if self.check_format_consistency(conversation):
                        valid_format_count += 1
                    
                    total_turns += len(conversation)
                    
                    # Evaluate responses
                    for turn in conversation:
                        if turn['from'] == 'assistant':
                            quality = self.evaluate_information_quality(turn['value'])
                            for metric, value in quality.items():
                                info_quality_scores[metric].append(value)
                    
                    # Check coherence
                    coherence = self.check_conversation_coherence(conversation)
                    for metric, value in coherence.items():
                        coherence_scores[metric].append(value)
                    
                    # Print sample analysis for first conversation
                    if total_conversations == 1:
                        print("Sample Conversation Analysis:")
                        for i, turn in enumerate(conversation):
                            role = "Student" if turn['from'] == 'human' else "Assistant"
                            print(f"\n{role}: {turn['value'][:100]}...")
                            if turn['from'] == 'assistant':
                                quality = self.evaluate_information_quality(turn['value'])
                                print("\nQuality Metrics:")
                                for metric, value in quality.items():
                                    print(f"- {metric}: {value}")
                        
                        print("\nCoherence Metrics:")
                        for metric, value in coherence.items():
                            print(f"- {metric}: {value:.2f}")
                
                except json.JSONDecodeError as e:
                    print(f"Error reading line: {e}")
                    continue
        
        # Calculate averages
        info_quality_avg = {
            metric: sum(values)/len(values) if values else 0 
            for metric, values in info_quality_scores.items()
        }
        
        coherence_avg = {
            metric: sum(values)/len(values) if values else 0 
            for metric, values in coherence_scores.items()
        }
        
        # Print overall analysis
        print("\n=== Dataset Quality Analysis ===")
        print(f"\nFormat Validation:")
        print(f"- Total conversations: {total_conversations}")
        print(f"- Valid format: {valid_format_count} ({valid_format_count*100/total_conversations:.1f}%)")
        print(f"- Average turns per conversation: {total_turns/total_conversations:.1f}")
        
        if self.format_issues:
            print("\nFormat Issues Found:")
            for issue in self.format_issues[:5]:  # Show first 5 issues
                print(f"- {issue}")
        
        print("\nInformation Quality (Averages):")
        for metric, value in info_quality_avg.items():
            if isinstance(value, bool):
                print(f"- {metric}: {value*100:.1f}%")
            else:
                print(f"- {metric}: {value:.2f}")
        
        print("\nConversation Coherence (Averages):")
        for metric, value in coherence_avg.items():
            print(f"- {metric}: {value:.2f}")
        
        # Training suitability score (0-100)
        format_score = valid_format_count/total_conversations * 25
        info_score = (sum(1 for v in info_quality_avg.values() if v > 0.5) / len(info_quality_avg)) * 25
        coherence_score = sum(coherence_avg.values()) / len(coherence_avg) * 25
        readability_score = info_quality_avg['readability'] * 0.25
        
        final_score = format_score + info_score + coherence_score + readability_score
        
        print(f"\nOverall Training Suitability Score: {final_score:.1f}/100")
        print("\nRecommendations:")
        if final_score >= 80:
            print("✓ Dataset is well-suited for fine-tuning")
        else:
            if format_score < 20:
                print("! Improve ChatML format consistency")
            if info_score < 20:
                print("! Enhance information quality and specificity")
            if coherence_score < 20:
                print("! Improve conversation flow and context utilization")
            if readability_score < 20:
                print("! Improve response clarity and structure")

if __name__ == "__main__":
    evaluator = DatasetEvaluator()
    evaluator.evaluate_dataset('dataset/study_abroad_dataset.jsonl')
