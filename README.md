# Study Abroad Dataset Generation Pipeline

Production-grade synthetic dataset generation system for study-abroad conversational guidance using Google Gemini API with comprehensive quality validation, topic balancing, and reproducibility controls.

## 🔗 Ecosystem

| Component | Link |
|-----------|------|
| Generated Dataset | [millat/StudyAbroadGPT-Dataset](https://huggingface.co/datasets/millat/StudyAbroadGPT-Dataset) |
| Fine-Tuned Model | [millat/StudyAbroadGPT-7B-LoRa-Kaggle](https://huggingface.co/millat/StudyAbroadGPT-7B-LoRa-Kaggle) |
| Training Code | [codermillat/StudyAbroadGPT](https://github.com/codermillat/StudyAbroadGPT) |
| Evaluation Companion | [LoRA Paper workspace](https://github.com/codermillat/LoRA-Paper) |
| Paper | [arXiv:2504.15610](https://arxiv.org/abs/2504.15610) |

## 📊 Output Artifact

- **Total Conversations**: 2,676
- **Train Split**: 2,274 (85%)
- **Test Split**: 402 (15%)
- **Average Turns per Conversation**: 5.2
- **Format**: JSONL (Hugging Face datasets library compatible)

## 📁 Repository Structure

```
study-abroad-dataset/
├── README.md                                    # This file
├── study_abroad_dataset/                        # Main Python package
│   ├── src/
│   │   ├── generator/
│   │   │   ├── conversation_generator.py        # Gemini API integration
│   │   │   ├── topic_manager.py                 # Topic balancing & selection
│   │   │   └── quality_validator.py             # Quality checking
│   │   ├── utils/
│   │   │   ├── config.py                        # Configuration & topic templates
│   │   │   ├── logger.py                        # Logging system
│   │   │   ├── progress_tracker.py              # Generation progress tracking
│   │   │   └── __init__.py
│   │   ├── main.py                              # Main entry point
│   │   ├── __main__.py                          # CLI interface
│   │   └── __init__.py
│   ├── examples/
│   │   └── basic_generation.py                  # Example usage
│   ├── API_SETUP.md                             # API configuration guide
│   └── README.md                                # Package README
├── dataset/                                     # Output directory
│   └── conversations.jsonl                      # Generated dataset
├── check_dataset.py                             # Dataset inspection utility
├── evaluate_for_training.py                     # Training readiness scoring
├── remove_simmiler.py                           # Duplicate removal script
├── validate_dataset.py                          # Full validation pipeline
├── verify_dataset.py                            # Dataset integrity checker
├── dataset_verifier.py                          # Structured verification
├── monitor_generation.py                        # Real-time progress monitor
└── requirements.txt                             # Python dependencies
```

## 🚀 Quick Start

### 1. Setup

```bash
# Clone repository
git clone https://github.com/codermillat/study-abroad-dataset.git
cd study-abroad-dataset

# Install dependencies
pip install -r requirements.txt

# Create .env file with API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 2. Generate Dataset

```bash
# Generate 50 conversations (quick test)
python study_abroad_dataset/src/main.py

# Generate full dataset (2676 conversations)
python study_abroad_dataset/src/__main__.py --total 2676

# With custom settings
python study_abroad_dataset/src/__main__.py \
    --total 2676 \
    --batch-size 5 \
    --max-retries 3
```

### 3. Validate Quality

```bash
# Check dataset structure
python check_dataset.py

# Full quality validation
python validate_dataset.py

# Score training readiness
python evaluate_for_training.py

# Verify integrity
python verify_dataset.py
```

### 4. Monitor Progress (in separate terminal)

```bash
python monitor_generation.py
```

## 🏗️ Architecture

### Generation Pipeline

```
Topic Selection
    ↓
Prompt Generation (Gemini API)
    ↓
Quality Validation
    ↓
Conversation Balancing
    ↓
JSONL Serialization
    ↓
dataset/conversations.jsonl
```

### Topic Configuration

Topics are pre-configured in `config.py` with balanced distribution targets:

```python
TOPICS = {
    "admission_requirements": {
        "weight": 1.0,
        "min_count": 500,
        "max_count": 1000,
        "subtopics": ["tests", "documents", "deadlines", "criteria"],
        "quality_threshold": 0.8
    },
    "scholarships": {...},
    "visa_immigration": {...},
    "accommodation_costs": {...},
    "university_selection": {...},
    # ... more topics
}
```

### Topic Manager

- **Weighted Selection**: Favors underrepresented topics
- **History Tracking**: Prevents consecutive repetition
- **Dynamic Balancing**: Adjusts weights based on progress
- **Target Distribution**: Respects min/max counts per topic

```python
from study_abroad_dataset.src.generator.topic_manager import TopicManager

topic_mgr = TopicManager()
topic, config = topic_mgr.select_next_topic(target_distribution)
```

### Quality Validator

Checks conversation structure, length, content patterns:

```python
from study_abroad_dataset.src.generator.quality_validator import QualityValidator

validator = QualityValidator()
quality_score, details = validator.validate_conversation(conversation)
if quality_score >= validator.QUALITY_THRESHOLD:
    # Conversation passes quality gates
```

Quality metrics:

- Minimum turn count: 4-6
- Response length: 100-1000 chars
- Reasoning patterns: Present
- Examples: At least 2
- Format: Valid JSON structure

## 🔄 Generation Process

### Single Conversation Generation

```python
from study_abroad_dataset.src.generator.conversation_generator import ConversationGenerator

gen = ConversationGenerator()
topic, config = topic_manager.select_next_topic()
conversation = gen.generate_conversation(topic, config)
# Result: {"conversations": [{"from": "human", "value": "..."}, ...]}
```

### Batch Generation with Resume Support

- Generation progress saved to `generation_progress.json`
- Resume from last checkpoint: `python ... --resume`
- Automatic retry with backoff on API failures
- Real-time WandB logging (optional)

### Conversation Format

```json
{
  "conversations": [
    {
      "from": "human",
      "value": "What documents do I need for a UK student visa?"
    },
    {
      "from": "assistant",
      "value": "To apply for a UK student visa, you typically need...\n\n1. Academic qualifications\n2. Proof of funds\n3. CAS letter from institution"
    }
  ]
}
```

## 🛠️ Utilities

### `check_dataset.py`

Quick inspection of dataset structure:

```bash
python check_dataset.py
# Output: Sample conversations, statistics, format validation
```

### `validate_dataset.py`

Comprehensive quality validation:

```bash
python validate_dataset.py
# Output: Quality report, metric summaries, issues found
```

### `evaluate_for_training.py`

Score readiness for model training:

```bash
python evaluate_for_training.py
# Output: Training suitability scores, recommendations
```

### `verify_dataset.py` / `dataset_verifier.py`

Structural integrity verification:

```bash
python verify_dataset.py --check-duplicates
python verify_dataset.py --remove-duplicates
# Output: Duplicate detection/removal report
```

### `remove_simmiler.py`

Remove near-duplicates via similarity:

```bash
python remove_simmiler.py --threshold 0.95
# Output: Cleaned dataset, duplicate statistics
```

### `monitor_generation.py`

Real-time progress monitoring dashboard:

```bash
python monitor_generation.py
# Output: Live progress, speed, ETA, topic distribution
```

## 📊 Quality Metrics

From companion evaluation artifacts:

- **Schema Validity**: 100% ✅
- **Role Alternation**: 100% ✅
- **Exact Duplicates**: 0 ✅
- **Train/Test Overlap**: 0 ✅
- **Near-Duplicates (TF-IDF ≥ 0.90)**: 0 ✅
- **Repeated Responses**: 2 groups
- **Empty Values**: 0 ✅

## 🔐 API Configuration

### Google Gemini API

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```
3. Or set environment variable:
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```

See [API_SETUP.md](study_abroad_dataset/API_SETUP.md) for detailed setup.

## 📈 Performance

| Setting | Value |
|---------|-------|
| API Model | Gemini 1.0 Pro |
| Generation Config Temperature | 0.7 |
| Max Output Tokens | 65,536 |
| Batch Size | 5 conversations |
| Delay Between Calls | 5 seconds |
| Max Retries | 3 |
| Estimated Time (2676 conversations) | ~4-6 hours |

## ⚠️ Reproducibility Notes

- Dataset is **synthetic** and generated via LLM
- Manual review was applied during initial generation
- No official policy sources were used (experimental dataset)
- Should be treated as domain-adaptation corpus, not authoritative source
- Validation against real university/immigration data recommended before production use

## 📝 Citation

If you use this dataset generation pipeline:

```bibtex
@misc{StudyAbroadGPT-Dataset,
  author = {Md Millat Hosen},
  title = {StudyAbroadGPT-Dataset},
  year = {2025},
  publisher = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/millat/StudyAbroadGPT-Dataset}},
  doi = {10.57967/hf/5257}
}

@article{hosen2025lora,
  title={A LoRA-Based Approach to Fine-Tuning LLMs for Educational Guidance in Resource-Constrained Settings},
  author={Hosen, Md Millat},
  journal={arXiv preprint arXiv:2504.15610},
  year={2025},
  doi={10.48550/arXiv.2504.15610}
}
```

## 🔐 License

MIT License

## 🤝 Contributing

Improvements, bug reports, and data contributions welcome. Please open an issue or PR.

## 📧 Questions?

See [API_SETUP.md](study_abroad_dataset/API_SETUP.md) for common issues or open an issue on GitHub.
