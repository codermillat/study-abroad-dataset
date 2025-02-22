import json
from collections import defaultdict
import statistics

def analyze_response_quality(response):
    """Analyze the quality of a response based on various metrics"""
    # Check response length (detailed responses typically > 100 words)
    words = len(response.split())
    
    # Check for structured content (sections, bullet points, etc.)
    has_structure = any(marker in response for marker in [':', '•', '-', '1.', '2.', 'First', 'Second', 'Finally'])
    
    # Check for specific details (numbers, dates, proper nouns)
    has_specifics = any(word.isupper() for word in response.split()) or \
                   any(char.isdigit() for char in response)
    
    return {
        'word_count': words,
        'has_structure': has_structure,
        'has_specifics': has_specifics,
    }

def check_topic_relevance(question, response):
    """Check if response contains key terms from the question"""
    question_keywords = set(word.lower() for word in question.split())
    response_words = set(word.lower() for word in response.split())
    overlap = question_keywords.intersection(response_words)
    return len(overlap) / len(question_keywords) if question_keywords else 0

def analyze_dataset(file_path):
    quality_metrics = {
        'conversations': [],
        'word_counts': [],
        'topic_relevance_scores': [],
        'structured_responses': 0,
        'specific_details': 0
    }
    
    topic_metrics = defaultdict(list)
    
    print("Analyzing dataset quality...\n")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        total_conversations = 0
        
        for line in f:
            try:
                data = json.loads(line)
                conversation = data.get('conversations', [])
                
                if not conversation:
                    continue
                
                total_conversations += 1
                conv_metrics = {'turns': []}
                
                # Identify topic from first question
                first_question = conversation[0]['value'].lower()
                topic = None
                if "visa" in first_question:
                    topic = "visa_immigration"
                elif "scholarship" in first_question:
                    topic = "scholarships"
                elif "job" in first_question or "work" in first_question:
                    topic = "job_opportunities"
                elif "university" in first_question:
                    topic = "university_selection"
                elif "requirements" in first_question or "admission" in first_question:
                    topic = "admission_requirements"
                
                # Analyze each turn in conversation
                for i in range(0, len(conversation), 2):
                    if i+1 >= len(conversation):
                        break
                        
                    question = conversation[i]['value']
                    response = conversation[i+1]['value']
                    
                    # Analyze response quality
                    quality = analyze_response_quality(response)
                    relevance = check_topic_relevance(question, response)
                    
                    quality_metrics['word_counts'].append(quality['word_count'])
                    quality_metrics['topic_relevance_scores'].append(relevance)
                    if quality['has_structure']:
                        quality_metrics['structured_responses'] += 1
                    if quality['has_specifics']:
                        quality_metrics['specific_details'] += 1
                    
                    conv_metrics['turns'].append({
                        'question': question[:100] + "...",
                        'word_count': quality['word_count'],
                        'relevance': relevance
                    })
                
                if topic:
                    topic_metrics[topic].append(conv_metrics)
                
                # Print detailed analysis of first conversation
                if total_conversations == 1:
                    print("Sample Conversation Analysis:")
                    for turn in conv_metrics['turns']:
                        print(f"\nQuestion: {turn['question']}")
                        print(f"Response stats:")
                        print(f"- Word count: {turn['word_count']}")
                        print(f"- Topic relevance: {turn['relevance']:.2f}")
                
            except json.JSONDecodeError as e:
                print(f"Error reading line: {e}")
                continue
    
    # Calculate overall metrics
    avg_word_count = statistics.mean(quality_metrics['word_counts'])
    avg_relevance = statistics.mean(quality_metrics['topic_relevance_scores'])
    
    print("\nOverall Dataset Quality Metrics:")
    print(f"Total conversations analyzed: {total_conversations}")
    print(f"Average response length: {avg_word_count:.1f} words")
    print(f"Average topic relevance: {avg_relevance:.2f}")
    print(f"Responses with clear structure: {quality_metrics['structured_responses']} ({quality_metrics['structured_responses']*100/(total_conversations*2):.1f}%)")
    print(f"Responses with specific details: {quality_metrics['specific_details']} ({quality_metrics['specific_details']*100/(total_conversations*2):.1f}%)")
    
    print("\nQuality by Topic:")
    for topic, convs in topic_metrics.items():
        topic_word_counts = []
        topic_relevance = []
        for conv in convs:
            for turn in conv['turns']:
                topic_word_counts.append(turn['word_count'])
                topic_relevance.append(turn['relevance'])
        
        if topic_word_counts:
            print(f"\n{topic}:")
            print(f"- Average response length: {statistics.mean(topic_word_counts):.1f} words")
            print(f"- Average relevance score: {statistics.mean(topic_relevance):.2f}")

if __name__ == "__main__":
    analyze_dataset('dataset/study_abroad_dataset.jsonl')
