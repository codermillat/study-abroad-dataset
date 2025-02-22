"""
Configuration module for the study abroad dataset generation system.
Contains all settings, parameters, and configurations used across the application.
"""

from typing import Dict, List, Any
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

class Config:
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # API Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Generation settings
    BATCH_SIZE = 5
    MAX_RETRIES = 3
    DELAY_BETWEEN_CALLS = 5  # seconds
    
    # Topic configuration with balanced distribution
    TOPICS: Dict[str, Dict[str, Any]] = {
        "admission_requirements": {
            "weight": 1.0,
            "min_count": 500,
            "max_count": 1000,
            "subtopics": ["tests", "documents", "deadlines", "criteria"],
            "quality_threshold": 0.8,
            "templates": [
                "What are the {test_name} requirements for {university}?",
                "How do I write a strong SOP for {program} at {university}?",
                "Can you explain the admission process for {university}?",
                "What documents do I need for applying to {program}?"
            ],
            "parameters": {
                "test_name": ["GRE", "IELTS", "TOEFL", "GMAT"],
                "university": ["MIT", "Stanford", "Oxford", "Cambridge"],
                "program": ["MS in Computer Science", "MBA", "MS in Data Science"]
            }
        },
        "scholarships": {
            "weight": 1.0,
            "min_count": 500,
            "max_count": 1000,
            "subtopics": ["merit-based", "need-based", "research", "country-specific"],
            "quality_threshold": 0.8,
            "templates": [
                "What scholarships are available for {nationality} students in {country}?",
                "How can I get a full scholarship for studying {program} in {country}?",
                "What are the merit-based scholarships at {university}?",
                "Tell me about need-based financial aid options in {country}"
            ],
            "parameters": {
                "nationality": ["Indian", "Chinese", "Nigerian", "Brazilian"],
                "country": ["USA", "UK", "Canada", "Germany", "Australia"],
                "program": ["Masters", "PhD", "MBA"],
                "university": ["MIT", "Stanford", "Oxford", "Cambridge"]
            }
        }
    }
    
    # Quality validation settings
    QUALITY_METRICS = {
        "min_words": 120,
        "max_words": 800,
        "min_sections": 2,
        "required_elements": [
            "##",  # Headers
            "*",   # Bullet points
            "-",   # Lists
        ],
        "quality_indicators": [
            "this is important because",
            "for example",
            "such as",
            "this means",
            "because",
            "therefore",
            "furthermore",
            "importantly",
            "specifically",
            "notably"
        ],
        "structure_weights": {
            "headers": 0.3,
            "lists": 0.2,
            "examples": 0.3,
            "reasoning": 0.2
        }
    }
    
    # Similarity detection settings
    SIMILARITY = {
        "threshold": 0.85,
        "ngram_range": (1, 2),
        "max_features": 5000
    }
    
    # Grammar and style settings
    GRAMMAR = {
        "check_spelling": True,
        "check_grammar": True,
        "formality_level": "academic",
        "style_guide": {
            "avoid_passive": True,
            "prefer_active_voice": True,
            "max_sentence_length": 40
        }
    }
    
    # Response structure requirements
    RESPONSE_STRUCTURE = {
        "required_sections": [
            "Introduction",
            "Main Content",
            "Examples & Evidence",
            "Action Steps"
        ],
        "section_requirements": {
            "Introduction": {
                "min_words": 30,
                "required_elements": ["preview points", "importance statement"]
            },
            "Main Content": {
                "min_words": 100,
                "required_elements": ["reasoning", "examples", "implications"]
            },
            "Examples & Evidence": {
                "min_items": 2,
                "required_elements": ["specific example", "data point"]
            },
            "Action Steps": {
                "min_items": 3,
                "required_elements": ["timeline", "clear steps"]
            }
        }
    }
    
    # Progress tracking settings
    PROGRESS = {
        "save_interval": 10,  # Save progress every 10 conversations
        "checkpoint_interval": 100,  # Create checkpoint every 100 conversations
        "log_level": "INFO"
    }

    @classmethod
    def validate_config(cls) -> bool:
        """Validate the configuration settings"""
        try:
            if not cls.GEMINI_API_KEY:
                print("GEMINI_API_KEY environment variable is required")
                print(f"Using config from: {cls.BASE_DIR / '.env'}")
                return False
            
            assert cls.BATCH_SIZE > 0, "BATCH_SIZE must be positive"
            assert cls.MAX_RETRIES > 0, "MAX_RETRIES must be positive"
            assert cls.DELAY_BETWEEN_CALLS >= 0, "DELAY_BETWEEN_CALLS must be non-negative"
            
            # Validate topic configuration
            for topic, config in cls.TOPICS.items():
                assert 0 < config["weight"] <= 1, f"Weight for {topic} must be between 0 and 1"
                assert config["min_count"] > 0, f"min_count for {topic} must be positive"
                assert config["max_count"] >= config["min_count"], f"max_count must be >= min_count for {topic}"
                assert len(config["templates"]) > 0, f"No templates defined for {topic}"
                assert len(config["parameters"]) > 0, f"No parameters defined for {topic}"
            
            return True
        except AssertionError as e:
            print(f"Configuration validation failed: {str(e)}")
            return False
