import time
import os
import json
from dataset_verifier import DatasetVerifier
from datetime import datetime

def monitor_dataset_generation(interval: int = 300):  # Check every 5 minutes
    """Monitor dataset generation progress and quality metrics"""
    dataset_path = "dataset/study_abroad_dataset.jsonl"
    print(f"Starting dataset generation monitor at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring {dataset_path}")
    print(f"Checking every {interval} seconds...")
    print("\nPress Ctrl+C to stop monitoring\n")
    
    last_size = 0
    last_check = 0
    verifier = DatasetVerifier(dataset_path)
    
    try:
        while True:
            current_time = time.time()
            
            # Check if file exists
            if not os.path.exists(dataset_path):
                print("\nWaiting for dataset file to be created...")
                time.sleep(30)
                continue
                
            # Get current file size
            current_size = os.path.getsize(dataset_path)
            
            # If file has changed and enough time has passed, validate
            if current_size != last_size and (current_time - last_check) >= interval:
                print(f"\n=== Validation Check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
                
                # Check status
                status = verifier.check_status()
                print(f"\nCurrent Progress:")
                print(f"- Conversations generated: {status['total_conversations']}")
                print(f"- Dataset size: {status['file_size'] / 1024:.1f} KB")
                print("\nTopic Distribution:")
                for topic, count in status['topics'].items():
                    print(f"- {topic}: {count}")
                
                # Save timestamped report
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_file = f"dataset/validation_report_{timestamp}.json"
                with open(report_file, 'w') as f:
                    json.dump(status, f, indent=2)
                
                # Run duplicate check
                verifier.check_duplicates()
                
                # Update tracking variables
                last_size = current_size
                last_check = current_time
                
            time.sleep(30)  # Check file size every 30 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError during monitoring: {e}")

if __name__ == "__main__":
    monitor_dataset_generation()
