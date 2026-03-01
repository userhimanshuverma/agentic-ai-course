"""
LLM Layer - Ollama integration with Mistral.
"""

import json
import time
import re
from typing import Dict, Any, Optional, Type
import requests

from ..utils.config import config
from ..utils.logger import logger


class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or config.OLLAMA_URL
        self.model = model or config.OLLAMA_MODEL
        self.timeout = config.LLM_TIMEOUT
        self.max_retries = config.LLM_MAX_RETRIES
    
    def generate(
        self,
        prompt: str,
        system: str = None,
        temperature: float = 0.7,
        format_schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: The prompt to send
            system: System message
            temperature: Sampling temperature
            format_schema: JSON schema for structured output
        
        Returns:
            Dict with 'text', 'tokens_used', and other metadata
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
            "options": {
                "num_ctx": 4096,
            }
        }
        
        if system:
            payload["system"] = system
        
        if format_schema:
            payload["format"] = "json"
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                elapsed_ms = (time.time() - start_time) * 1000
                
                result = {
                    "text": data.get("response", ""),
                    "tokens_used": data.get("eval_count", 0),
                    "total_duration_ms": data.get("total_duration", 0) / 1_000_000,
                    "load_duration_ms": data.get("load_duration", 0) / 1_000_000,
                    "prompt_eval_count": data.get("prompt_eval_count", 0),
                    "elapsed_ms": elapsed_ms
                }
                
                logger.log_llm_call(
                    goal_id=getattr(self, '_current_goal_id', None),
                    prompt_type="generate",
                    tokens_used=result["tokens_used"]
                )
                
                return result
                
            except requests.exceptions.Timeout:
                logger.warning(f"Ollama timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise TimeoutError("Ollama API timeout")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except requests.exceptions.ConnectionError:
                logger.error(f"Cannot connect to Ollama at {self.base_url}")
                raise ConnectionError(
                    f"Cannot connect to Ollama at {self.base_url}. "
                    "Make sure Ollama is running: ollama serve"
                )
            
            except Exception as e:
                logger.error(f"Ollama error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system: str = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            prompt: The prompt to send
            schema: JSON schema for validation
            system: System message
            temperature: Sampling temperature
        
        Returns:
            Parsed JSON dict
        """
        # Add schema to prompt
        schema_prompt = f"""
You must respond with valid JSON that matches this schema:
{json.dumps(schema, indent=2)}

Do not include any other text, only the JSON response.
"""
        
        full_prompt = prompt + "\n\n" + schema_prompt
        
        result = self.generate(
            prompt=full_prompt,
            system=system,
            temperature=temperature,
            format_schema=schema
        )
        
        # Parse JSON response
        text = result["text"].strip()
        
        # Try to extract JSON if wrapped in markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            parsed = json.loads(text)
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {text[:200]}")
            raise ValueError(f"Invalid JSON response: {str(e)}")


class LLMManager:
    """Manages LLM interactions with retry and validation."""
    
    def __init__(self):
        self.client = OllamaClient()
    
    def create_plan(self, goal: str, available_tools: str) -> Dict[str, Any]:
        """Create an execution plan for a goal."""
        system = """You are a planning agent. Break down goals into concrete steps.
Each step should be actionable and may use available tools."""
        
        prompt = f"""Goal: {goal}

Available Tools:
{available_tools}

Create a step-by-step plan to achieve this goal. Each step should have:
- step_number: sequential number
- description: what this step does
- tool_call: (optional) tool to use with arguments
- expected_output: what this step should produce

Respond with a JSON object matching the plan schema."""
        
        from ..utils.schema import PLAN_SCHEMA
        
        return self.client.generate_structured(
            prompt=prompt,
            schema=PLAN_SCHEMA,
            system=system,
            temperature=0.3
        )
    
    def reflect_on_execution(
        self,
        goal: str,
        plan: Dict[str, Any],
        results: list
    ) -> Dict[str, Any]:
        """Reflect on execution results."""
        system = """You are a reflection agent. Analyze execution results and provide insights."""
        
        results_summary = "\n".join([
            f"Step {r['step_number']}: {'✓' if r['success'] else '✗'} - {str(r['output'])[:100]}"
            for r in results
        ])
        
        prompt = f"""Goal: {goal}

Execution Results:
{results_summary}

Analyze the execution:
1. Was the goal achieved?
2. What was accomplished?
3. What lessons were learned?
4. What could be improved?

Respond with a JSON object matching the reflection schema."""
        
        from ..utils.schema import REFLECTION_SCHEMA
        
        return self.client.generate_structured(
            prompt=prompt,
            schema=REFLECTION_SCHEMA,
            system=system,
            temperature=0.3
        )
    
    def check_model_available(self) -> bool:
        """Check if the model is available in Ollama."""
        try:
            response = requests.get(
                f"{self.client.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check if model name is in available models
            for name in model_names:
                if self.client.model in name or name in self.client.model:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check model availability: {str(e)}")
            return False


# Global LLM manager
llm_manager = LLMManager()
