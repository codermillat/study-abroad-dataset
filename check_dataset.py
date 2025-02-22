import json
from collections import Counter

def analyze_dataset(file_path):
    topics = Counter()
    total_conversations = 0
    total_turns = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                total_conversations += 1
                conversation = data.get('conversations', [])
                total_turns += len(conversation)
                
                # Get the first question to identify topic
                if conversation and conversation[0]['from'] == 'human':
                    first_question = conversation[0]['value']
                    if "visa" in first_question.lower():
                        topics["visa_immigration"] += 1
                    elif "scholarship" in first_question.lower():
                        topics["scholarships"] += 1
                    elif "job" in first_question.lower() or "work" in first_question.lower():
                        topics["job_opportunities"] += 1
                    elif "university" in first_question.lower():
                        topics["university_selection"] += 1
                    elif "requirements" in first_question.lower() or "admission" in first_question.lower():
                        topics["admission_requirements"] += 1
                
                # Print first conversation as sample
                if total_conversations == 1:
                    print("\nSample Conversation:")
                    for turn in conversation:
                        role = "Student" if turn['from'] == 'human' else "Assistant"
                        print(f"\n{role}: {turn['value'][:200]}...")
            
            except json.JSONDecodeError as e:
                print(f"Error reading line: {e}")
                continue

    print("\nDataset Statistics:")
    print(f"Total conversations: {total_conversations}")
    print(f"Average turns per conversation: {total_turns/total_conversations if total_conversations else 0:.1f}")
    print("\nTopic Distribution:")
    for topic, count in topics.items():
        print(f"{topic}: {count}")

if __name__ == "__main__":
    analyze_dataset('dataset/study_abroad_dataset.jsonl')
