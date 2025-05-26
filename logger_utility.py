import os
import logging
from datetime import datetime
from typing import Any, Dict

class LoggerUtility:
    def __init__(self, log_dir: str = "log"):
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(log_dir, f"run_{timestamp}.log")
        self.logger = logging.getLogger(f"HistoricalMonumentsAI_{timestamp}")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(log_file, encoding="utf-8")  # Ensure UTF-8 encoding
        fh.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(fh)
        self.console = logging.StreamHandler()
        self.console.setFormatter(formatter)
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            self.logger.addHandler(self.console)

    def log_user_question(self, question: str):
        self.logger.info(f"[USER QUESTION] User asked: {question}")

    def log_tool_call(self, tool_name: str, input_vars: Dict[str, Any]):
        self.logger.info(f"[TOOL CALL] Tool: {tool_name} | Input Parameters: {input_vars}")

    def log_tool_response(self, tool_name: str, response: Any):
        self.logger.info(f"[TOOL RESPONSE] Tool: {tool_name} | Response: {response}")

    def log_llm_response(self, response: str):
        self.logger.info(f"[LLM RESPONSE] {response}")

    def log_agent_response(self, response: str):
        self.logger.info(f"[AGENT RESPONSE] {response}")

# Singleton instance for easy import
logger_utility = LoggerUtility()
