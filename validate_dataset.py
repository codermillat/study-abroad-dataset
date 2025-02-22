import argparse
from dataset_verifier import DatasetVerifier

def main():
    parser = argparse.ArgumentParser(description='Verify and manage dataset')
    parser.add_argument('--check-duplicates', action='store_true',
                      help='Check for duplicate conversations')
    parser.add_argument('--remove-duplicates', action='store_true',
                      help='Remove duplicate conversations')
    parser.add_argument('--status', action='store_true',
                      help='Show dataset status')
    parser.add_argument('--dataset', default='dataset/study_abroad_dataset.jsonl',
                      help='Path to dataset file')
                      
    args = parser.parse_args()
    verifier = DatasetVerifier(args.dataset)
    
    if args.status:
        status = verifier.check_status()
        print("\nDataset Status:")
        print(f"Total conversations: {status['total_conversations']}")
        print(f"File size: {status['file_size']/1024:.1f} KB")
        print(f"Last modified: {status['last_modified']}")
        print("\nTopic Distribution:")
        for topic, count in status['topics'].items():
            print(f"- {topic}: {count}")
            
    if args.check_duplicates:
        verifier.check_duplicates()
        
    if args.remove_duplicates:
        verifier.remove_duplicates()
        
    # If no actions specified, show status by default
    if not (args.status or args.check_duplicates or args.remove_duplicates):
        status = verifier.check_status()
        print("\nDataset Status:")
        print(f"Total conversations: {status['total_conversations']}")
        print(f"File size: {status['file_size']/1024:.1f} KB")
        print(f"Last modified: {status['last_modified']}")
        print("\nTopic Distribution:")
        for topic, count in status['topics'].items():
            print(f"- {topic}: {count}")

if __name__ == "__main__":
    main()
