"""
Quality validation module for generated conversations.
Handles real-time validation of content structure, relevance, and quality metrics.
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Optional
from ..utils.config import Config
from ..utils.logger import logger

class QualityValidator:
    """
    Validates generated conversations for quality, structure,
    and content requirements in real-time.
    """
    
    def __init__(self):
        self.config = Config
        self.quality_metrics = self.config.QUALITY_METRICS
        self.structure_requirements = self.config.RESPONSE_STRUCTURE
    
    def validate_conversation(self, conversation: Dict) -> Tuple[bool, Dict[str, float]]:
        """
        Validate a complete conversation against all quality criteria.
        Returns (passed, scores) tuple.
        """
        try:
            # Extract assistant responses for validation
            responses = [
                turn["value"] for turn in conversation["conversations"]
                if turn["from"] == "assistant"
            ]
            
            # Validate each response
            response_scores = []
            for response in responses:
                structure_score = self._validate_structure(response)
                content_score = self._validate_content(response)
                quality_score = self._validate_quality_indicators(response)
                
                response_scores.append({
                    "structure": structure_score,
                    "content": content_score,
                    "quality": quality_score,
                    "overall": np.mean([structure_score, content_score, quality_score])
                })
            
            # Calculate overall conversation scores
            overall_scores = {
                "structure": np.mean([s["structure"] for s in response_scores]),
                "content": np.mean([s["content"] for s in response_scores]),
                "quality": np.mean([s["quality"] for s in response_scores]),
                "overall": np.mean([s["overall"] for s in response_scores])
            }
            
            # Check if conversation passes minimum thresholds
            passed = (
                overall_scores["overall"] >= 0.7 and
                overall_scores["structure"] >= 0.6 and
                overall_scores["content"] >= 0.6 and
                overall_scores["quality"] >= 0.6
            )
            
            logger.debug(
                "Conversation validation complete",
                {"passed": passed, "scores": overall_scores}
            )
            
            return passed, overall_scores
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False, {}
    
    def _validate_structure(self, response: str) -> float:
        """
        Validate response structure against requirements.
        Returns score between 0 and 1.
        """
        score = 0
        total_checks = 4  # Number of structural elements we're checking
        
        # Check section headers
        if "##" in response:
            score += 0.25
            # Check for all required sections
            sections_found = set()
            for section in self.structure_requirements["required_sections"]:
                if re.search(f"##.*{section}", response, re.IGNORECASE):
                    sections_found.add(section)
            section_ratio = len(sections_found) / len(self.structure_requirements["required_sections"])
            score += 0.25 * section_ratio
        
        # Check bullet points and lists
        if any(marker in response for marker in ["*", "-", "1."]):
            score += 0.25
            # Check list depth and formatting
            list_lines = len(re.findall(r"^[\s-]*[\*\-\d\.]", response, re.MULTILINE))
            score += 0.25 * min(1, list_lines / 5)  # Expect at least 5 list items
            
        return score
    
    def _validate_content(self, response: str) -> float:
        """
        Validate response content quality and relevance.
        Returns score between 0 and 1.
        """
        score = 0
        checks_passed = 0
        total_checks = 5
        
        # Check word count
        word_count = len(response.split())
        if self.quality_metrics["min_words"] <= word_count <= self.quality_metrics["max_words"]:
            checks_passed += 1
        
        # Check for examples
        if any(marker in response.lower() for marker in ["for example", "such as", "like"]):
            checks_passed += 1
        
        # Check for reasoning statements
        if any(marker in response.lower() for marker in ["because", "therefore", "this means"]):
            checks_passed += 1
        
        # Check for specific details
        if re.search(r"\b\d+%|\b\d{4}\b|\$\d+", response):  # Numbers, years, amounts
            checks_passed += 1
        
        # Check for proper formatting
        if re.search(r"\*\*.*\*\*|##.*|`.*`", response):  # Bold text, headers, or code
            checks_passed += 1
        
        return checks_passed / total_checks
    
    def _validate_quality_indicators(self, response: str) -> float:
        """
        Check for presence of quality indicators in the response.
        Returns score between 0 and 1.
        """
        score = 0
        response_lower = response.lower()
        
        # Check for quality indicator phrases
        indicators_found = sum(
            1 for indicator in self.quality_metrics["quality_indicators"]
            if indicator in response_lower
        )
        
        # Calculate base score from indicators
        indicator_score = min(1.0, indicators_found / 3)  # Expect at least 3 indicators
        score += indicator_score * 0.6  # 60% of score from indicators
        
        # Check additional quality elements
        additional_score = 0
        
        # Check for data points or statistics
        if re.search(r"\d+%|\d+ students|\d+ universities", response_lower):
            additional_score += 0.1
        
        # Check for institution names
        if re.search(r"university of|institute of|\b[A-Z][a-z]+ University\b", response):
            additional_score += 0.1
        
        # Check for structured information
        if re.search(r"first.*second.*third|step 1.*step 2|finally", response_lower):
            additional_score += 0.1
        
        # Check for contextual references
        if re.search(r"according to|research shows|studies indicate", response_lower):
            additional_score += 0.1
        
        score += additional_score
        
        return min(1.0, score)
    
    def validate_response_structure(self, response: str, section: str) -> bool:
        """
        Validate a specific section of a response against its requirements.
        """
        requirements = self.structure_requirements["section_requirements"].get(section, {})
        
        # Check word count if specified
        if "min_words" in requirements:
            word_count = len(response.split())
            if word_count < requirements["min_words"]:
                return False
        
        # Check required elements
        if "required_elements" in requirements:
            for element in requirements["required_elements"]:
                element_patterns = self._get_element_patterns(element)
                if not any(re.search(pattern, response, re.IGNORECASE) 
                          for pattern in element_patterns):
                    return False
        
        # Check minimum items if specified
        if "min_items" in requirements:
            items = len(re.findall(r"^[\s-]*[\*\-\d\.]", response, re.MULTILINE))
            if items < requirements["min_items"]:
                return False
        
        return True
    
    def _get_element_patterns(self, element: str) -> List[str]:
        """Get regex patterns for checking required elements"""
        patterns = {
            "preview points": [
                r"will discuss|will cover|will explore",
                r"key (points|aspects|factors)",
                r"following (points|aspects|topics)"
            ],
            "importance statement": [
                r"important because|critical for|essential to",
                r"plays a vital role|significant impact",
                r"key importance|crucial factor"
            ],
            "reasoning": [
                r"because|therefore|consequently",
                r"this means|this leads to|this results in",
                r"due to|as a result|hence"
            ],
            "examples": [
                r"for example|such as|like",
                r"instance|specifically|namely",
                r"to illustrate|consider"
            ],
            "implications": [
                r"implications|impact|effect",
                r"leads to|results in|causes",
                r"consequently|as a result"
            ],
            "specific example": [
                r"\b[A-Z][a-z]+ University\b",
                r"\$\d+,\d+|\d+%|\d+ students",
                r"in \d{4}|as of \d{4}"
            ],
            "data point": [
                r"\d+%|\d+\+?",
                r"\$\d+(?:,\d+)*(?:\.\d+)?",
                r"increased|decreased|grew by"
            ],
            "timeline": [
                r"weeks|months|years",
                r"deadline|due date|by",
                r"early|mid|late \d{4}"
            ],
            "clear steps": [
                r"step \d|first|second|third",
                r"begin by|next|finally",
                r"\d\. |\* |- "
            ]
        }
        return patterns.get(element, [r""])
