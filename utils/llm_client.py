"""
LLM Client supporting open-source models (Llama, Mistral) via Ollama or HuggingFace
"""
import json
import logging
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified client for open-source LLMs.
    Supports:
    - Ollama (local deployment of Llama, Mistral, etc.)
    - HuggingFace Inference API
    """

    def __init__(self):
        self.provider = settings.llm_provider
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "huggingface":
            self._init_huggingface()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

        logger.info(f"Initialized LLM client with provider: {self.provider}")

    def _init_ollama(self):
        """Initialize Ollama client"""
        try:
            import ollama
            self.client = ollama.Client(host=settings.ollama_base_url)
            self.model = settings.ollama_model
            logger.info(f"Ollama client initialized with model: {self.model}")
        except ImportError:
            logger.error("Ollama package not installed. Run: pip install ollama")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise

    def _init_huggingface(self):
        """Initialize HuggingFace client"""
        try:
            from langchain_community.llms import HuggingFaceHub
            if not settings.huggingface_api_token:
                raise ValueError("HUGGINGFACE_API_TOKEN not set in environment")

            self.client = HuggingFaceHub(
                repo_id=settings.huggingface_model,
                huggingfacehub_api_token=settings.huggingface_api_token,
                model_kwargs={
                    "temperature": self.temperature,
                    "max_new_tokens": self.max_tokens,
                }
            )
            self.model = settings.huggingface_model
            logger.info(f"HuggingFace client initialized with model: {self.model}")
        except ImportError:
            logger.error("HuggingFace dependencies not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Generate text completion from the LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt for instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: If True, request JSON output

        Returns:
            Generated text response
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        if self.provider == "ollama":
            return self._generate_ollama(prompt, system_prompt, temp, max_tok, json_mode)
        elif self.provider == "huggingface":
            return self._generate_huggingface(prompt, system_prompt, temp, max_tok)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> str:
        """Generate using Ollama"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                format="json" if json_mode else "",
            )

            content = response["message"]["content"]
            logger.debug(f"Ollama response: {content[:200]}...")
            return content

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    def _generate_huggingface(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate using HuggingFace"""
        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        try:
            response = self.client(full_prompt)
            logger.debug(f"HuggingFace response: {response[:200]}...")
            return response
        except Exception as e:
            logger.error(f"HuggingFace generation failed: {e}")
            raise

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output

        Args:
            prompt: User prompt
            system_prompt: System prompt
            schema: Optional JSON schema to validate against

        Returns:
            Parsed JSON response
        """
        # Add JSON instruction to prompt
        json_instruction = "\n\nRespond ONLY with valid JSON. Do not include any explanation or markdown formatting."

        if schema:
            json_instruction += f"\n\nFollow this schema:\n{json.dumps(schema, indent=2)}"

        full_prompt = prompt + json_instruction

        response = self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            json_mode=True if self.provider == "ollama" else False,
        )

        # Parse JSON from response
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            parsed = json.loads(json_str)
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            # Return empty dict or raise
            raise ValueError(f"Invalid JSON response from LLM: {response[:200]}")

    def generate_with_examples(
        self,
        prompt: str,
        examples: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate with few-shot examples

        Args:
            prompt: User prompt
            examples: List of {"input": "...", "output": "..."} examples
            system_prompt: System prompt

        Returns:
            Generated response
        """
        # Build few-shot prompt
        few_shot = ""
        for i, example in enumerate(examples, 1):
            few_shot += f"\n\nExample {i}:\nInput: {example['input']}\nOutput: {example['output']}"

        full_prompt = f"{few_shot}\n\nNow respond to this:\nInput: {prompt}\nOutput:"

        return self.generate(prompt=full_prompt, system_prompt=system_prompt)


# Global LLM client instance
llm_client = LLMClient()
