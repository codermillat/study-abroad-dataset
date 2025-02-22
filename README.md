<<<<<<< HEAD
# study-abroad-dataset
=======
# Study Abroad Conversational Dataset Generator

A comprehensive system for generating high-quality conversational datasets focused on study abroad topics, with built-in quality monitoring and validation.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Setup](#setup)
- [File Structure](#file-structure)
- [Usage](#usage)
- [Configuration](#configuration)
- [Quality Monitoring](#quality-monitoring)
- [Output Format](#output-format)

## Overview

This system generates realistic conversations between students and study abroad consultants. It covers various topics including:
- Admission Requirements
- Scholarships
- University Selection
- Visa & Immigration
- Job Opportunities

## Features

- Multi-turn conversations with context awareness
- Structured responses with reasoning and examples
- Quality validation and monitoring
- Progress tracking and error handling
- Resumable generation process
- Comprehensive quality metrics

## System Requirements

- Python 3.8+
- Required packages:
  ```
  google-generativeai
  tqdm
  python-dotenv
  beautifulsoup4
  requests
  ```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd study-abroad-dataset-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create .env file with your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## File Structure

### Core Components

1. `main.py`
   - Main conversation generation logic
   - Topic configuration and templates
   - Response structuring and formatting
   
2. `generate_full_dataset.py`
   - Resumable dataset generation
   - Progress tracking
   - Batch processing
   - Error handling

3. `validate_dataset.py`
   - Quality metrics calculation
   - Format validation
   - Content analysis
   - Detailed reporting

4. `monitor_generation.py`
   - Real-time progress monitoring
   - Periodic quality checks
   - Status reporting
   - Error logging

5. `analyze_quality.py`
   - Detailed quality analysis
   - Training suitability scoring
   - Conversation coherence checking
   - Example validation

6. `verify_dataset.py`
   - Dataset integrity verification
   - Structure validation
   - Format consistency checks

### Output Files

- `dataset/conversations.jsonl`: Generated conversations
- `dataset/validation_report_*.json`: Quality validation reports
- `dataset/generation_progress.json`: Progress tracking
- `dataset/generation_errors.log`: Error logs

## Usage

### 1. Dataset Generation

#### Start New Generation
```bash
# Generate 100 conversations
python generate_full_dataset.py

# Monitor generation progress (in a separate terminal)
python monitor_generation.py
```

#### Pause and Resume

1. To pause generation:
   - Press Ctrl+C in the terminal running generate_full_dataset.py
   - The system will complete the current conversation and save progress
   - Progress is automatically saved in dataset/generation_progress.json

2. To resume generation:
   ```bash
   # Simply run the generator again
   python generate_full_dataset.py
   ```
   - The system will:
     * Load previous progress from generation_progress.json
     * Continue from the last successful conversation
     * Maintain topic distribution balance
     * Skip completed topics

#### Duplicate Prevention

The system prevents duplicates through multiple mechanisms:

1. Progress Tracking:
   - Tracks completed conversations per topic
   - Maintains conversation hashes to detect duplicates
   - Skips previously completed topics

2. Topic Management:
   ```python
   # Configure in generate_full_dataset.py
   generator = ResumableDatasetGenerator(
       output_dir="dataset",
       batch_size=5,
       deduplicate=True  # Enable duplicate checking
   )
   ```

3. Manual Control:
   ```bash
   # Check for duplicates in existing dataset
   python verify_dataset.py --check-duplicates

   # Remove duplicates from dataset
   python verify_dataset.py --remove-duplicates
   ```

4. Duplicate Detection Methods:
   - Content similarity checking
   - Conversation structure comparison
   - Template variation tracking

### 2. Validate Existing Dataset

```bash
# Run validation
python validate_dataset.py

# Analyze quality metrics
python analyze_quality.py
```

### 3. Quick Generation (10 conversations)

```bash
python main.py
```

## Configuration

### Topic Configuration (`main.py`)

```python
"TOPICS": {
    "admission_requirements": {
        "templates": [...],
        "parameters": {...}
    },
    # Add more topics...
}
```

### Generation Settings (`generate_full_dataset.py`)

```python
generator = ResumableDatasetGenerator(
    output_dir="dataset",
    batch_size=5  # Adjust batch size
)
generator.generate_dataset(
    total_conversations=100,  # Total conversations to generate
    max_retries=3  # Max retries per conversation
)
```

### Quality Thresholds (`validate_dataset.py`)

```python
QUALITY_THRESHOLDS = {
    "min_turns": 4,
    "min_response_length": 100,
    "min_reasoning_patterns": 1,
    "min_examples": 2
}
```

## Quality Monitoring

The system provides real-time quality monitoring:

1. Format Validation:
   - ChatML format compliance
   - Turn structure consistency
   - Role label accuracy

2. Content Quality:
   - Response length
   - Reasoning patterns
   - Example usage
   - Context references

3. Conversation Coherence:
   - Topic consistency
   - Context utilization
   - Turn balance

4. Metrics Tracked:
   - Total conversations
   - Valid conversations
   - Average turns
   - Response length
   - Topic distribution
   - Quality scores

## Output Format

### Conversation Format (JSONL)

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "What are the GRE requirements for MIT?"
    },
    {
      "from": "assistant",
      "value": "## GRE Requirements for MIT\n..."
    },
    // More turns...
  ]
}
```

### Validation Report Format

```json
{
  "dataset_stats": {
    "total_conversations": 100,
    "valid_conversations": 98,
    "average_turns": 6.0,
    "average_response_length": 312.5
  },
  "quality_metrics": {
    "reasoning": 0.85,
    "examples": 0.92,
    "context": 0.78
  }
}
```

## Best Practices

1. Monitor Generation:
   - Always run monitor_generation.py alongside generation
   - Check validation reports periodically
   - Watch for error logs
   - Use Ctrl+C for safe pausing

2. Progress Management:
   - Keep generation_progress.json for resume capability
   - Back up partial datasets before interrupting
   - Monitor topic distribution balance
   - Check duplicate statistics in validation reports

3. Resuming Large Datasets:
   ```bash
   # Check generation status
   python verify_dataset.py --status

   # Clean dataset and restart with duplicate prevention
   python verify_dataset.py --remove-duplicates
   python generate_full_dataset.py
   python monitor_generation.py

   # Resume with adjusted parameters
   python generate_full_dataset.py --batch-size 3 --max-retries 5
   ```

4. Duplicate Handling:
   - Regular duplicate checking during generation
   - Periodic dataset validation
   - Manual review of similar conversations
   - Backup before duplicate removal

2. Quality Checks:
   - Validate dataset after generation
   - Review sample conversations
   - Check topic distribution

3. Error Handling:
   - Monitor error logs
   - Adjust batch size if needed
   - Use resume capability for large datasets

## Contributing

Contributions welcome! Please read the contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
>>>>>>> 89124ce (Initial commit: Study Abroad Dataset Generator)
