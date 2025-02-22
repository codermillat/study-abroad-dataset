import argparse
from dataset_verifier import DatasetVerifier

def main():
    parser = argparse.ArgumentParser(
        description='Verify and analyze the study abroad dataset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                            # Show dataset status
  %(prog)s --check-duplicates         # Check for duplicates
  %(prog)s --remove-duplicates        # Remove duplicates
  %(prog)s --status                   # Show detailed status
  %(prog)s --dataset other_file.jsonl # Use different dataset file
        """
    )
    
    group = parser.add_argument_group('actions')
    group.add_argument('--check-duplicates', action='store_true',
                      help='Check for duplicate conversations')
    group.add_argument('--remove-duplicates', action='store_true',
                      help='Remove duplicate conversations (creates backup)')
    group.add_argument('--status', action='store_true',
                      help='Show detailed dataset status')
    
    parser.add_argument('--dataset', default='dataset/study_abroad_dataset.jsonl',
                      help='Path to dataset file (default: %(default)s)')
    
    args = parser.parse_args()
    
    # Create verifier
    verifier = DatasetVerifier(args.dataset)
    
    # Always show basic status
    print("\n=== Dataset Verification ===")
    print(f"Dataset: {args.dataset}")
    
    # Get and show status
    status = verifier.check_status()
    print(f"\nBasic Status:")
    print(f"- Total conversations: {status['total_conversations']}")
    print(f"- File size: {status['file_size']/1024:.1f} KB")
    print(f"- Last modified: {status['last_modified']}")
    
    # If no specific actions requested, show detailed status
    if not (args.check_duplicates or args.remove_duplicates or args.status):
        print("\nTopic Distribution:")
        for topic, count in status['topics'].items():
            print(f"- {topic}: {count}")
        print("\nUse --help to see all available commands")
        
    # Handle specific actions
    if args.status:
        print("\nDetailed Topic Distribution:")
        for topic, count in status['topics'].items():
            percentage = (count / status['total_conversations'] * 100) if status['total_conversations'] > 0 else 0
            print(f"- {topic}: {count} ({percentage:.1f}%)")
            
    if args.check_duplicates:
        verifier.check_duplicates()
        
    if args.remove_duplicates:
        verifier.remove_duplicates()

if __name__ == "__main__":
    main()
