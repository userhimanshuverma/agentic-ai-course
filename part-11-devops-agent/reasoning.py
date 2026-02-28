"""
AI Reasoning Module - Uses Ollama with Mistral
==============================================

Simple module that connects to Ollama's local API for AI reasoning.
"""

import json
import logging
import requests
from typing import Dict, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ReasoningResult:
    """AI reasoning result"""
    action: str
    reasoning: str
    tool_to_use: str
    parameters: Dict[str, Any]
    confidence: float
    is_complete: bool


class AIReasoner:
    """
    Simple AI reasoner using Ollama's local Mistral.
    
    Example:
        reasoner = AIReasoner()
        result = reasoner.analyze(metrics, "Check CPU")
        print(result.action)
    """
    
    def __init__(self, url: str = "http://localhost:11434"):
        """Initialize with Ollama URL"""
        self.url = url
        self.model = "mistral"
        logger.info(f"AI Reasoner initialized (Ollama: {url})")
    
    def analyze(self, metrics: Dict[str, Any], goal: str) -> ReasoningResult:
        """
        Analyze metrics and recommend action.
        
        Args:
            metrics: System metrics dict
            goal: Monitoring goal
        
        Returns:
            ReasoningResult with action recommendation
        """
        prompt = self._build_prompt(metrics, goal)
        response = self._ask_mistral(prompt)
        return self._parse_response(response)
    
    def _build_prompt(self, metrics: Dict[str, Any], goal: str) -> str:
        """Build prompt for Mistral"""
        return f"""You are a DevOps monitoring assistant.

Goal: {goal}

System Metrics:
{json.dumps(metrics, indent=2, default=str)}

Available Tools:
- get_cpu_metrics: Get CPU usage
- get_memory_metrics: Get RAM usage
- get_disk_metrics: Get disk usage
- get_process_metrics: Get top processes
- get_all_metrics: Get all metrics

Respond in JSON:
{{
    "action": "what to do",
    "reasoning": "why",
    "tool_to_use": "tool_name",
    "parameters": {{}},
    "confidence": 0.8,
    "is_complete": false
}}"""
    
    def _ask_mistral(self, prompt: str) -> str:
        """Send prompt to Ollama Mistral"""
        try:
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 200}
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            # Fallback response
            return json.dumps({
                "action": "Check system metrics",
                "reasoning": "Using fallback due to Ollama error",
                "tool_to_use": "get_all_metrics",
                "parameters": {},
                "confidence": 0.5,
                "is_complete": True
            })
    
    def _parse_response(self, response: str) -> ReasoningResult:
        """Parse Mistral's JSON response"""
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return ReasoningResult(
                    action=data.get("action", "Continue monitoring"),
                    reasoning=data.get("reasoning", ""),
                    tool_to_use=data.get("tool_to_use", "get_all_metrics"),
                    parameters=data.get("parameters", {}),
                    confidence=data.get("confidence", 0.5),
                    is_complete=data.get("is_complete", False)
                )
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON, using fallback")
        
        # Fallback
        return ReasoningResult(
            action="Continue monitoring",
            reasoning=response[:100] if response else "No response",
            tool_to_use="get_all_metrics",
            parameters={},
            confidence=0.5,
            is_complete=False
        )
