import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import google.generativeai as genai
from typing import List, Dict, Any
import re
from urllib.parse import urljoin
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class StudyAbroadDataGenerator:
    def __init__(self):
        self.model = self._initialize_model()
        self.config = self._load_config()
        self.scraped_faqs = {}
        
    def _initialize_model(self):
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 65536,
        }
        try:
            return genai.GenerativeModel(
                model_name="gemini-1.0-pro",  # Updated to use stable version
                generation_config=generation_config,
            )
        except Exception as e:
            print(f"Error initializing model: {e}")
            return None
            
    def generate_conversation(self, topic: str) -> Dict[str, List[Dict[str, str]]]:
        """Generate a complete multi-turn conversation with improved context utilization and reasoning"""
        if not self.model:
            print("Model not initialized properly")
            return None

        def exponential_backoff(attempt: int, max_delay: int = 60) -> float:
            """Calculate delay with exponential backoff and random jitter"""
            delay = min(max_delay, 5 * (2 ** attempt))  # 5, 10, 20, 40, 60...
            jitter = random.uniform(0, 0.1 * delay)  # 10% jitter
            return delay + jitter

        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            try:
                topic_config = self.config["TOPICS"][topic]
                template = random.choice(topic_config["templates"])
                params = {k: random.choice(v) for k, v in topic_config["parameters"].items()}
                
                # Format the initial question
                initial_question = template.format(**params)
                
                # Generate initial response
                initial_response = self.model.generate_content(self._get_initial_prompt(initial_question))
                if not initial_response or not initial_response.text:
                    raise Exception("No response generated for initial question")
                    
                initial_response_text = initial_response.text
                
                # Initialize conversation with first Q&A
                conversation = [
                    {"from": "human", "value": initial_question},
                    {"from": "assistant", "value": initial_response_text}
                ]
                
                # Generate follow-up questions
                follow_ups = self._generate_follow_up_questions(topic, initial_question, initial_response_text)
                context_summary = [initial_response_text]
                
                for follow_up in follow_ups:
                    # Create context-aware prompt
                    context = "\n\n".join(context_summary)
                    follow_up_response = self.model.generate_content(self._get_follow_up_prompt(follow_up, context, topic))
                    if follow_up_response and follow_up_response.text:
                        response_text = follow_up_response.text
                        conversation.extend([
                            {"from": "human", "value": follow_up},
                            {"from": "assistant", "value": response_text.strip()}
                        ])
                        context_summary.append(response_text)
                
                return {"conversations": conversation}
                
            except KeyError as e:
                print(f"Error: Missing key in config for topic {topic}: {e}")
                return None
            except Exception as e:
                error_msg = str(e).lower()
                if any(term in error_msg for term in ['rate', 'quota', 'limit', 'timeout']):
                    # API rate limit hit - apply backoff
                    delay = exponential_backoff(attempt)
                    print(f"\nAPI rate limit hit, waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                    attempt += 1
                    if attempt < max_attempts:
                        continue
                
                print(f"Error generating conversation for topic {topic}: {e}")
                return None
        
        return None  # All attempts failed

    def _get_initial_prompt(self, question: str) -> str:
        return f"""As an expert study abroad consultant, provide a comprehensive response to: {question}

CRITICAL REQUIREMENTS:
Each section MUST include:
1. At least one explicit reasoning statement using:
   - "This is important because..."
   - "This results in..."
   - "The reason for this is..."
   - "This means that..."
   - "Due to this factor..."

2. At least one specific example with:
   - Real university names
   - Actual dates or deadlines
   - Specific numbers or statistics
   - Real-world scenarios

RESPONSE STRUCTURE:
## Introduction
* Acknowledge the question
* Preview 3-4 key points
* Include WHY these points matter

## Main Content (2-3 sections)
For each major point:
1. Clear statement
2. Reasoning explanation
3. Supporting evidence
4. Specific example
5. Practical implication

## Evidence & Examples
* Statistical data point
* University-specific example
* Student success story
* Timeline or deadline
* Numerical facts

## Action Steps
1. Clear next steps
2. Timeline if applicable
3. Success metrics
4. Common pitfalls

FORMATTING:
* Use markdown (##, *, -)
* Short paragraphs (2-3 sentences)
* Bullet points for lists
* Clear section headings"""

    def _get_follow_up_prompt(self, follow_up: str, context: str, topic: str) -> str:
        return f"""Continue the conversation. The student asks: {follow_up}

PREVIOUS CONTEXT:
{context}

RESPONSE REQUIREMENTS:
1. Context Integration (MANDATORY)
   Start with:
   "Building on our previous discussion about [specific topic], let's explore..."
   
   Include at least 3 references:
   * "As we discussed earlier regarding [specific point]..."
   * "This connects directly to the [specific aspect] we covered..."
   * "To expand on the earlier point about [specific detail]..."

2. Reasoning Pattern (REQUIRED in each section)
   Every major point must include:
   * Cause: "Because of [reason]..."
   * Effect: "This leads to..."
   * Implication: "This means that..."

3. Evidence & Examples (MINIMUM 2 per response)
   * Specific data points
   * Real institution names
   * Actual requirements
   * Success stories

4. Topic Continuity
   * Maintain focus on {topic}
   * Connect new information to previous points
   * Build logical progression
   * Address student's specific concerns

5. Actionable Insights
   * Clear recommendations
   * Step-by-step guidance
   * Timeline if applicable
   * Success metrics

FORMAT:
## Main Point
* Key details
* Supporting information

### Sub-section
1. First step/point
2. Next step/point"""

    def _load_config(self) -> Dict:
        """Load the configuration for topics and their templates"""
        return {
            "TOPICS": {
                "admission_requirements": {
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
                },
                "university_selection": {
                    "templates": [
                        "Which universities in {country} are best for {program}?",
                        "What factors should I consider when choosing a university for {program}?",
                        "How do I find universities that match my profile for {program}?"
                    ],
                    "parameters": {
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"],
                        "program": ["Computer Science", "Business Analytics", "Engineering"]
                    }
                },
                "visa_immigration": {
                    "templates": [
                        "What is the student visa process for {country}?",
                        "How long does it take to get a student visa for {country}?",
                        "What documents are needed for {country} student visa?",
                        "Can I work part-time on a student visa in {country}?"
                    ],
                    "parameters": {
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"]
                    }
                },
                "job_opportunities": {
                    "templates": [
                        "What are the job prospects after {program} in {country}?",
                        "How does the post-study work visa work in {country}?",
                        "Tell me about internship opportunities for international students in {country}",
                        "Which {program} specializations have the best job market in {country}?"
                    ],
                    "parameters": {
                        "program": ["MS in Computer Science", "MBA", "MS in Data Science"],
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"]
                    }
                },
                "living_costs": {
                    "templates": [
                        "What is the cost of living for students in {city}, {country}?",
                        "How much should I budget monthly for {city}?",
                        "How expensive is student accommodation in {city}?",
                        "What are typical student expenses in {country}?"
                    ],
                    "parameters": {
                        "city": ["Boston", "London", "Toronto", "Berlin", "Sydney"],
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"]
                    }
                },
                "cultural_adaptation": {
                    "templates": [
                        "How can I adjust to student life in {country}?",
                        "What cultural differences should I prepare for in {country}?",
                        "Tips for overcoming culture shock in {country}?",
                        "How to make friends and network as an international student?"
                    ],
                    "parameters": {
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"]
                    }
                },
                "healthcare": {
                    "templates": [
                        "What health insurance do I need as a student in {country}?",
                        "How does the healthcare system work for international students in {country}?",
                        "What medical coverage is provided by universities in {country}?",
                        "Mental health resources for international students in {country}?"
                    ],
                    "parameters": {
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"]
                    }
                },
                "language_preparation": {
                    "templates": [
                        "How can I improve my {language} before studying in {country}?",
                        "What language support services do universities offer?",
                        "Do I need to take additional language courses in {country}?",
                        "Tips for academic writing in {language}?"
                    ],
                    "parameters": {
                        "language": ["English", "German", "French"],
                        "country": ["USA", "UK", "Canada", "Germany", "France"]
                    }
                },
                "research_opportunities": {
                    "templates": [
                        "What research opportunities are available for {program} students?",
                        "How to find research assistantships in {field}?",
                        "Research funding options for international students?",
                        "How to approach professors for research opportunities?"
                    ],
                    "parameters": {
                        "program": ["Masters", "PhD", "Undergraduate"],
                        "field": ["Computer Science", "Engineering", "Life Sciences", "Social Sciences"]
                    }
                },
                "housing": {
                    "templates": [
                        "What are the housing options near {university}?",
                        "On-campus vs off-campus housing in {city}?",
                        "How to find affordable student accommodation in {city}?",
                        "What documents do I need to rent in {country}?"
                    ],
                    "parameters": {
                        "university": ["MIT", "Stanford", "Oxford", "Cambridge"],
                        "city": ["Boston", "London", "Toronto", "Berlin", "Sydney"],
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"]
                    }
                },
                "transportation": {
                    "templates": [
                        "How to get around as a student in {city}?",
                        "Public transportation options near {university}?",
                        "Student discounts for transportation in {country}?",
                        "Bicycle-friendly campuses and cities for students?"
                    ],
                    "parameters": {
                        "city": ["Boston", "London", "Toronto", "Berlin", "Sydney"],
                        "university": ["MIT", "Stanford", "Oxford", "Cambridge"],
                        "country": ["USA", "UK", "Canada", "Germany", "Australia"]
                    }
                },
                "student_life": {
                    "templates": [
                        "What student clubs and organizations are popular at {university}?",
                        "Sports and fitness facilities for students at {university}?",
                        "Social activities and events for international students?",
                        "Best places for students to hang out in {city}?"
                    ],
                    "parameters": {
                        "university": ["MIT", "Stanford", "Oxford", "Cambridge"],
                        "city": ["Boston", "London", "Toronto", "Berlin", "Sydney"]
                    }
                }
            }
        }

    def _generate_follow_up_questions(self, topic: str, initial_query: str, initial_response: str) -> List[str]:
        """Generate contextual follow-up questions based on topic and initial response"""
        follow_ups = {
            "admission_requirements": [
                "What specific documents do I need to prepare?",
                "Can you help me understand the timeline for applications?",
                "What makes a strong application stand out?"
            ],
            "scholarships": [
                "Are there any university-specific scholarships I should know about?",
                "What are the typical scholarship deadlines?",
                "How competitive are these scholarships?"
            ],
            "university_selection": [
                "What factors should I prioritize when choosing between universities?",
                "What are the living costs and campus culture like?",
                "How important are university rankings?"
            ],
            "visa_immigration": [
                "What's the processing time for visa applications?",
                "Are there any common reasons for visa rejection?",
                "What financial documents do I need for the visa?"
            ],
            "job_opportunities": [
                "What are the typical salary ranges in this field?",
                "How do I find internships during my studies?",
                "Which companies commonly hire international graduates?"
            ],
            "living_costs": [
                "What are the most expensive aspects of student life?",
                "How can I reduce my living expenses?",
                "Are there student discounts available?"
            ],
            "cultural_adaptation": [
                "What are common cultural misunderstandings?",
                "How can I participate in local cultural activities?",
                "What cultural etiquette should I be aware of?"
            ],
            "healthcare": [
                "What does the student health insurance cover?",
                "How do I find English-speaking doctors?",
                "What's the process for medical emergencies?"
            ],
            "language_preparation": [
                "What level of proficiency do I need?",
                "Are there language support groups?",
                "How can I practice with native speakers?"
            ],
            "research_opportunities": [
                "What are the funding requirements?",
                "How competitive are research positions?",
                "What skills do I need to develop?"
            ],
            "housing": [
                "What are typical rental contract terms?",
                "How far in advance should I start looking?",
                "What areas are safe and convenient for students?"
            ],
            "transportation": [
                "What are the best student transit passes?",
                "How reliable is public transportation?",
                "Is it worth bringing/buying a bicycle?"
            ],
            "student_life": [
                "What activities happen during orientation?",
                "How can I join student organizations?",
                "What facilities are open 24/7?"
            ]
        }
        return random.sample(follow_ups.get(topic, []), 2)

    def generate_dataset(self, num_conversations: int = 10) -> None:
        """Generate the complete dataset with conversations across all topics"""
        dataset = []
        topics = list(self.config["TOPICS"].keys())
        
        # Generate synthetic conversations
        print("\nGenerating synthetic conversations...")
        with tqdm(total=num_conversations) as pbar:
            conversations_per_topic = max(1, num_conversations // len(topics))
            for topic in topics:
                successful_conversations = 0
                attempts = 0
                max_attempts = conversations_per_topic * 2
                
                while successful_conversations < conversations_per_topic and attempts < max_attempts:
                    conversation = self.generate_conversation(topic)
                    if conversation and len(conversation["conversations"]) >= 4:  # Ensure at least 2 Q&A pairs
                        dataset.append(conversation)
                        successful_conversations += 1
                        pbar.update(1)
                    attempts += 1
                    time.sleep(5)  # Increased delay for rate limiting
        
        # Save the dataset
        print("\nSaving dataset...")
        os.makedirs("dataset", exist_ok=True)
        
        output_file = "dataset/study_abroad_dataset.jsonl"
        with open(output_file, "w", encoding='utf-8') as f:
            for conversation in dataset:
                f.write(json.dumps(conversation, ensure_ascii=False) + "\n")
        print(f"\nDataset generated successfully!")
        print(f"Total conversations: {len(dataset)}")
        print(f"Saved to: {output_file}")

def main():
    try:
        generator = StudyAbroadDataGenerator()
        generator.generate_dataset(num_conversations=10)
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
