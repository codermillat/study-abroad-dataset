"""
Main conversation generation module.
Handles the generation of high-quality, diverse Q&A conversations
with real-time validation and topic balancing.
"""

import os
import time
import random
import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the root directory to Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from src.utils.config import Config
from src.utils.logger import logger
from src.generator.quality_validator import QualityValidator
from src.generator.topic_manager import TopicManager

# Load environment variables
load_dotenv()

class InvalidAPIKeyError(Exception):
    """Raised when the API key is invalid or missing."""
    pass

class ConversationGenerator:
    """
    Generates high-quality study abroad Q&A conversations
    with proper structure, content validation, and topic balancing.
    """
    
    def __init__(self):
        self.validator = QualityValidator()
        self.topic_manager = TopicManager()
        self.model = self._initialize_model()
        
        # Validate API key on initialization
        if not self._validate_api_key():
            raise InvalidAPIKeyError(
                "Invalid or missing API key. Please set a valid GEMINI_API_KEY in your .env file."
            )
    
    def _validate_api_key(self) -> bool:
        """Validate the API key format and presence"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return False
            
        # Basic format validation (this is a simplified check)
        if not api_key.startswith('AI') or len(api_key) < 20:
            logger.error("API key appears to be in wrong format")
            return False
            
        return True
    
    def _initialize_model(self):
        """Initialize the Gemini model with appropriate configuration"""
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 65536,
        }
        
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("GEMINI_API_KEY not found in environment")
                return None
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.0-pro",
                generation_config=generation_config
            )
            
            # Test the model with a simple prompt
            test_response = model.generate_content("Say 'test' if you can hear me.")
            if not test_response or not test_response.text:
                logger.error("Model failed to generate test response")
                return None
                
            return model
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            return None
    
    def generate_conversation(self, topic: Optional[str] = None) -> Optional[Dict]:
        """Generate a complete multi-turn conversation for a given or selected topic"""
        try:
            if not self.model:
                logger.error("Model not initialized")
                return None
            
            # Select topic if not provided
            if not topic:
                topic, topic_config = self.topic_manager.select_next_topic()
            else:
                topic_config = Config.TOPICS[topic]
            
            # Select subtopic
            subtopic = self.topic_manager.select_subtopic(topic)
            
            # Generate initial question
            template = random.choice(topic_config["templates"])
            params = {
                k: random.choice(v) 
                for k, v in topic_config["parameters"].items()
            }
            initial_question = template.format(**params)
            
            # Generate initial response with retry logic
            initial_response = self._generate_response_with_retry(
                self._get_initial_prompt(initial_question, topic, subtopic)
            )
            
            if not initial_response:
                return None
            
            # Initialize conversation
            conversation = {
                "conversations": [
                    {"from": "human", "value": initial_question},
                    {"from": "assistant", "value": initial_response}
                ],
                "metadata": {
                    "topic": topic,
                    "subtopic": subtopic,
                    "template": template,
                    "parameters": params
                }
            }
            
            # Generate follow-up exchanges
            context = [initial_response]
            follow_ups = self._generate_follow_up_questions(topic, subtopic, initial_question, initial_response)
            
            for follow_up in follow_ups:
                follow_up_response = self._generate_response_with_retry(
                    self._get_follow_up_prompt(follow_up, context, topic, subtopic)
                )
                
                if follow_up_response:
                    conversation["conversations"].extend([
                        {"from": "human", "value": follow_up},
                        {"from": "assistant", "value": follow_up_response}
                    ])
                    context.append(follow_up_response)
            
            # Validate final conversation
            passed, scores = self.validator.validate_conversation(conversation)
            if not passed:
                logger.debug(
                    "Conversation failed validation",
                    {"topic": topic, "scores": scores}
                )
                return None
            
            # Record successful generation
            self.topic_manager.record_generation(topic, subtopic)
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error generating conversation: {str(e)}")
            return None
    
    def _generate_response_with_retry(
        self, 
        prompt: str, 
        max_retries: int = 3,
        base_delay: float = 2.0
    ) -> Optional[str]:
        """Generate response with exponential backoff retry logic"""
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            try:
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
                
            except Exception as e:
                attempt += 1
                last_error = e
                
                # Check for specific error types
                error_str = str(e).lower()
                if "api_key_invalid" in error_str:
                    logger.error("Invalid API key. Please check your configuration.")
                    break  # Don't retry on invalid API key
                elif "quota" in error_str or "rate" in error_str:
                    # Rate limiting - use longer delays
                    delay = base_delay * (4 ** attempt) + random.uniform(0, 2)
                else:
                    # Other errors - use standard exponential backoff
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                
                if attempt < max_retries:
                    logger.warning(
                        f"Generation attempt {attempt} failed, retrying in {delay:.1f}s",
                        {"error": str(e)}
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"All generation attempts failed: {str(e)}")
                    
        if last_error:
            logger.error(f"Final error: {str(last_error)}")
        return None

    # ... [rest of the methods remain the same] ...
