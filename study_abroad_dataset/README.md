# Study Abroad Q&A Dataset Generator

A robust system for generating high-quality, diverse Q&A conversations about studying abroad. The generator ensures balanced topic distribution, real-time quality validation, and proper conversation structure.

## Features

- **Topic Balancing**: Ensures even distribution across different study abroad topics and subtopics
- **Quality Control**: Real-time validation of content structure, relevance, and quality metrics
- **Natural Conversations**: Multi-turn exchanges with context-aware follow-up questions
- **Scalable Architecture**: Concurrent generation with proper error handling and recovery
- **Progress Tracking**: Detailed logging and progress monitoring with checkpointing

## Project Structure

```
study_abroad_dataset/
├── src/
│   ├── generator/
│   │   ├── conversation_generator.py   # Core generation logic
│   │   ├── topic_manager.py           # Topic balancing
│   │   └── quality_validator.py        # Content validation
│   ├── utils/
│   │   ├── config.py                  # Configuration management
│   │   ├── logger.py                  # Enhanced logging
│   │   └── progress_tracker.py        # Generation progress
│   └── main.py                        # Main orchestration
├── data/                              # Input data directory
├── output/                            # Generated datasets
├── logs/                              # Log files
└── requirements.txt                   # Dependencies
```

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```

## Usage

Generate dataset with default settings:
```bash
python src/main.py
```

Customize generation:
```bash
python src/main.py \
  --total-conversations 10000 \
  --batch-size 5 \
  --output-dir custom/output/path
```

### Command Line Arguments

- `--total-conversations`: Total number of conversations to generate (default: 5000)
- `--batch-size`: Number of concurrent generations (default: 5)
- `--output-dir`: Custom output directory (default: output/)

## Output Format

The generator produces JSONL files with the following structure:

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "What are the GRE requirements for MIT?"
    },
    {
      "from": "assistant",
      "value": "## Introduction\n* Here's what you need..."
    },
    // Additional turns...
  ],
  "metadata": {
    "topic": "admission_requirements",
    "subtopic": "tests",
    "template": "What are the {test_name} requirements for {university}?",
    "parameters": {
      "test_name": "GRE",
      "university": "MIT"
    }
  }
}
```

## Quality Metrics

Each generated conversation is validated against:

1. **Structure Requirements**:
   - Proper section headers
   - Bullet points and lists
   - Required components per section

2. **Content Quality**:
   - Word count limits
   - Presence of examples
   - Reasoning statements
   - Specific details and statistics

3. **Topic Relevance**:
   - Topic adherence
   - Subtopic coverage
   - Context consistency

4. **Conversation Flow**:
   - Natural progression
   - Context integration
   - Proper follow-up handling

## Monitoring

The system provides detailed logging:

- Real-time progress updates
- Topic distribution metrics
- Quality check results
- Error reporting and recovery status

Logs are stored in the `logs/` directory with timestamp-based filenames.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Implement your changes
4. Write/update tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details
