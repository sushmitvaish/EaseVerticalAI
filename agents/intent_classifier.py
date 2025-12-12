"""
Intent Classifier Agent
Determines user intent from natural language input
"""
import logging
from pathlib import Path
from typing import Dict, Any

from utils.llm_client import llm_client

logger = logging.getLogger(__name__)


class IntentClassifierAgent:
    """
    Agent that classifies user intent from natural language input
    Determines if user wants customers, partners, or both
    """

    def __init__(self):
        self.prompt_template = self._load_prompt_template()
        logger.info("Intent Classifier Agent initialized")

    def _load_prompt_template(self) -> str:
        """Load the intent classification prompt template"""
        prompt_file = Path("prompts/intent_classifier.txt")
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()
        else:
            logger.warning(f"Prompt file not found: {prompt_file}")
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Fallback prompt if file not found"""
        return """Classify the user's intent.
User Input: {user_input}

Respond with JSON:
{{"intent": "customer|partner|both|unclear", "confidence": 0.0-1.0, "reasoning": "explanation"}}
"""

    def classify(self, user_input: str) -> Dict[str, Any]:
        """
        Classify user intent

        Args:
            user_input: Natural language input from user

        Returns:
            Dictionary with intent, confidence, and reasoning
        """
        logger.info(f"Classifying intent for input: {user_input[:100]}...")

        # Format prompt
        prompt = self.prompt_template.format(user_input=user_input)

        try:
            # Get LLM response
            response = llm_client.generate_json(
                prompt=prompt,
                system_prompt="You are an intent classification system. Always respond with valid JSON.",
            )

            # Validate response structure
            required_fields = ["intent", "confidence", "reasoning"]
            if not all(field in response for field in required_fields):
                logger.error(f"Missing required fields in response: {response}")
                return self._get_default_intent()

            # Validate intent value
            valid_intents = ["customer", "partner", "both", "unclear"]
            if response["intent"] not in valid_intents:
                logger.warning(f"Invalid intent value: {response['intent']}, defaulting to 'unclear'")
                response["intent"] = "unclear"
                response["confidence"] = 0.3

            logger.info(f"Classified intent: {response['intent']} (confidence: {response['confidence']})")
            return response

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return self._get_default_intent()

    def _get_default_intent(self) -> Dict[str, Any]:
        """Return default intent when classification fails"""
        return {
            "intent": "unclear",
            "confidence": 0.0,
            "reasoning": "Failed to classify intent due to error"
        }


# Global instance
intent_classifier = IntentClassifierAgent()
