"""
Basic example demonstrating how to use the dataset generator.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import from src
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src import (
    ConversationGenerator,
    Config,
    logger
)

async def generate_sample_conversations(count: int = 5):
    """Generate a small sample of conversations"""
    # Initialize generator
    generator = ConversationGenerator()
    
    print(f"\nGenerating {count} sample conversations...")
    
    # Generate conversations
    for i in range(count):
        print(f"\nGenerating conversation {i+1}/{count}")
        
        conversation = await generator.generate_conversation()
        if conversation:
            # Print the conversation
            print("\nGenerated Conversation:")
            for turn in conversation["conversations"]:
                role = "Student" if turn["from"] == "human" else "Assistant"
                print(f"\n{role}: {turn['value'][:100]}...")
            
            print(f"\nMetadata: {conversation['metadata']}")
        else:
            print("Failed to generate conversation")
        
        print("\n" + "="*80)

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Verify API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return
    
    # Verify configuration
    if not Config.validate_config():
        print("Error: Invalid configuration")
        return
    
    # Generate sample conversations
    asyncio.run(generate_sample_conversations())
    
    print("\nSample generation complete!")
    print("""
Next steps:
1. Review the generated conversations above
2. Adjust configuration in src/utils/config.py if needed
3. Run the full generator:
   python src/main.py --total-conversations 1000
""")

if __name__ == "__main__":
    main()
