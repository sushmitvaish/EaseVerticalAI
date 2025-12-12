"""
Prompt Tracing Utility
Logs and tracks LLM prompts and responses for optimization
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptTracer:
    """
    Utility for tracing LLM prompts and responses
    Helps optimize prompts and analyze performance
    """

    def __init__(self, log_dir: str = "data/prompt_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        logger.info(f"Prompt tracer initialized: {self.session_file}")

    def log_prompt(
        self,
        agent_name: str,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a prompt and its response

        Args:
            agent_name: Name of the agent making the request
            prompt: The prompt sent to LLM
            response: The response from LLM
            metadata: Additional metadata (e.g., temperature, model, timing)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }

        try:
            # Append to JSONL file
            with open(self.session_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            logger.debug(f"Logged prompt for {agent_name}")

        except Exception as e:
            logger.error(f"Failed to log prompt: {e}")

    def log_error(
        self,
        agent_name: str,
        prompt: str,
        error: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a failed prompt

        Args:
            agent_name: Name of the agent
            prompt: The prompt that failed
            error: Error message
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt,
            "error": error,
            "status": "failed",
            "metadata": metadata or {}
        }

        try:
            with open(self.session_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            logger.debug(f"Logged error for {agent_name}")

        except Exception as e:
            logger.error(f"Failed to log error: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of all prompts in this session

        Returns:
            Dictionary with statistics
        """
        if not self.session_file.exists():
            return {"error": "No log file found"}

        total_prompts = 0
        failed_prompts = 0
        agent_stats = {}

        try:
            with open(self.session_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    total_prompts += 1

                    agent = entry.get("agent", "unknown")
                    if agent not in agent_stats:
                        agent_stats[agent] = {"total": 0, "failed": 0}

                    agent_stats[agent]["total"] += 1

                    if entry.get("status") == "failed":
                        failed_prompts += 1
                        agent_stats[agent]["failed"] += 1

            report = {
                "session_file": str(self.session_file),
                "total_prompts": total_prompts,
                "successful_prompts": total_prompts - failed_prompts,
                "failed_prompts": failed_prompts,
                "success_rate": (total_prompts - failed_prompts) / total_prompts if total_prompts > 0 else 0,
                "agent_stats": agent_stats
            }

            return report

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {"error": str(e)}


# Global prompt tracer instance
prompt_tracer = PromptTracer()
