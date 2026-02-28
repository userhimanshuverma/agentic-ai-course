"""
Part 11: DevOps Monitoring Agent - Reasoning Module
===================================================

This module handles AI-powered reasoning using Mistral.
It provides:
- Local inference with transformers
- Cloud API fallback (HuggingFace Inference API)
- Structured reasoning output
- Action recommendations

The reasoning engine analyzes system metrics and suggests actions.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReasoningMode(Enum):
    """Available reasoning modes"""
    OLLAMA = "ollama"    # Use Ollama local API (recommended)
    LOCAL = "local"      # Use local Mistral model via transformers
    API = "api"          # Use HuggingFace Inference API
    MOCK = "mock"        # Use mock responses (for testing)


@dataclass
class ReasoningResult:
    """Structured reasoning result"""
    action: str
    reasoning: str
    tool_to_use: str
    parameters: Dict[str, Any]
    confidence: float
    is_complete: bool


class MistralReasoner:
    """
    Mistral-powered reasoning engine for DevOps monitoring.
    
    This class provides AI-powered analysis of system metrics
    and recommends actions. It supports both local inference
    and cloud API modes.
    
    Example:
        reasoner = MistralReasoner(mode=ReasoningMode.MOCK)
        result = reasoner.analyze_metrics(metrics, goal="Check CPU")
        print(result.action)
    """
    
    def __init__(self, mode: ReasoningMode = ReasoningMode.MOCK, api_token: Optional[str] = None, ollama_url: str = "http://localhost:11434"):
        """
        Initialize the reasoning engine.
        
        Args:
            mode: Reasoning mode (OLLAMA, LOCAL, API, or MOCK)
            api_token: HuggingFace API token (required for API mode)
            ollama_url: Ollama API URL (default: http://localhost:11434)
        """
        self.mode = mode
        self.api_token = api_token or os.getenv("HF_API_TOKEN")
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = None
        self.tokenizer = None
        
        if mode == ReasoningMode.OLLAMA:
            if not self._check_ollama():
                logger.warning("Ollama not available, falling back to MOCK mode")
                self.mode = ReasoningMode.MOCK
        elif mode == ReasoningMode.LOCAL:
            self._init_local_model()
        elif mode == ReasoningMode.API:
            if not self.api_token:
                logger.warning("No API token provided, falling back to MOCK mode")
                self.mode = ReasoningMode.MOCK
        
        logger.info(f"MistralReasoner initialized in {self.mode.value} mode")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                logger.info(f"Ollama available with models: {model_names}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ollama check failed: {e}")
            return False
    
    def _generate_ollama(self, prompt: str) -> str:
        """Generate response using Ollama API"""
        try:
            import requests
            
            url = f"{self.ollama_url}/api/generate"
            
            payload = {
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 200
                }
            }
            
            logger.info("Sending request to Ollama...")
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._generate_mock(prompt)
    
    def _init_local_model(self):
        """Initialize local Mistral model via transformers (loads on first use)"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            logger.info("Loading Mistral model via transformers (this may take a moment)...")
            
            # Use a smaller model for faster loading
            # For production, use "mistralai/Mistral-7B-Instruct-v0.2"
            model_name = "HuggingFaceTB/SmolLM-135M-Instruct"  # Lightweight for demo
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            
            logger.info("Model loaded successfully")
            
        except ImportError:
            logger.error("transformers library not installed. Run: pip install transformers")
            logger.warning("Falling back to MOCK mode")
            self.mode = ReasoningMode.MOCK
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning("Falling back to MOCK mode")
            self.mode = ReasoningMode.MOCK
    
    def _generate_local(self, prompt: str) -> str:
        """Generate response using local model"""
        if self.model is None or self.tokenizer is None:
            return self._generate_mock(prompt)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Format for instruction-following models
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
            
        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            return self._generate_mock(prompt)
    
    def _generate_api(self, prompt: str) -> str:
        """Generate response using HuggingFace Inference API"""
        try:
            import requests
            
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {self.api_token}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            
            return str(result)
            
        except Exception as e:
            logger.error(f"API generation failed: {e}")
            return self._generate_mock(prompt)
    
    def _generate_mock(self, prompt: str) -> str:
        """
        Generate mock response for testing without AI.
        
        This simulates AI reasoning with rule-based responses.
        Perfect for learning and testing without GPU/API.
        """
        prompt_lower = prompt.lower()
        
        # Parse metrics from prompt
        cpu_percent = self._extract_value(prompt, "cpu", "percent")
        mem_percent = self._extract_value(prompt, "memory", "percent")
        disk_percent = self._extract_value(prompt, "disk", "percent")
        
        # Determine action based on metrics
        if cpu_percent and cpu_percent > 80:
            return json.dumps({
                "action": "Investigate high CPU usage",
                "reasoning": f"CPU is at {cpu_percent}%, which is above the 80% threshold. This indicates potential performance issues.",
                "tool_to_use": "get_process_metrics",
                "parameters": {"top_n": 5},
                "confidence": 0.9,
                "is_complete": False
            })
        
        elif mem_percent and mem_percent > 85:
            return json.dumps({
                "action": "Check for memory-intensive processes",
                "reasoning": f"Memory usage is at {mem_percent}%, approaching critical levels.",
                "tool_to_use": "get_process_metrics",
                "parameters": {"top_n": 10},
                "confidence": 0.85,
                "is_complete": False
            })
        
        elif disk_percent and disk_percent > 90:
            return json.dumps({
                "action": "Free up disk space",
                "reasoning": f"Disk is {disk_percent}% full. Critical storage situation.",
                "tool_to_use": "get_disk_metrics",
                "parameters": {},
                "confidence": 0.95,
                "is_complete": False
            })
        
        elif "check" in prompt_lower or "monitor" in prompt_lower:
            return json.dumps({
                "action": "Collect comprehensive system metrics",
                "reasoning": "Performing routine system health check. All metrics appear normal.",
                "tool_to_use": "get_all_metrics",
                "parameters": {},
                "confidence": 0.8,
                "is_complete": True
            })
        
        else:
            return json.dumps({
                "action": "Continue monitoring",
                "reasoning": "System metrics are within normal ranges. No immediate action required.",
                "tool_to_use": "get_all_metrics",
                "parameters": {},
                "confidence": 0.75,
                "is_complete": True
            })
    
    def _extract_value(self, prompt: str, metric_type: str, field: str) -> Optional[float]:
        """Extract a numeric value from the prompt text"""
        import re
        
        # Look for patterns like "cpu": {"percent": 45.5}
        pattern = rf'{metric_type}.*?{field}["\']?\s*:\s*([\d.]+)'
        match = re.search(pattern, prompt, re.IGNORECASE)
        
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _parse_response(self, response: str) -> ReasoningResult:
        """Parse AI response into structured result"""
        try:
            # Try to parse as JSON
            if "{" in response and "}" in response:
                # Extract JSON from response
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return ReasoningResult(
                    action=data.get("action", "Continue monitoring"),
                    reasoning=data.get("reasoning", "No specific reasoning provided"),
                    tool_to_use=data.get("tool_to_use", "get_all_metrics"),
                    parameters=data.get("parameters", {}),
                    confidence=data.get("confidence", 0.5),
                    is_complete=data.get("is_complete", False)
                )
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON")
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
        
        # Fallback: return default result
        return ReasoningResult(
            action="Continue monitoring",
            reasoning=response[:200] if response else "No response",
            tool_to_use="get_all_metrics",
            parameters={},
            confidence=0.5,
            is_complete=False
        )
    
    def analyze_metrics(self, metrics: Dict[str, Any], goal: str) -> ReasoningResult:
        """
        Analyze system metrics and recommend actions.
        
        Args:
            metrics: Dictionary of system metrics
            goal: The monitoring goal
        
        Returns:
            ReasoningResult with recommended action
        
        Example:
            metrics = {'cpu': {'percent': 85}, 'memory': {'percent': 60}}
            result = reasoner.analyze_metrics(metrics, "Check system health")
            print(result.action)  # "Investigate high CPU usage"
        """
        # Build prompt for the AI
        prompt = self._build_prompt(metrics, goal)
        
        # Generate response based on mode
        if self.mode == ReasoningMode.OLLAMA:
            response = self._generate_ollama(prompt)
        elif self.mode == ReasoningMode.LOCAL:
            response = self._generate_local(prompt)
        elif self.mode == ReasoningMode.API:
            response = self._generate_api(prompt)
        else:
            response = self._generate_mock(prompt)
        
        # Parse and return structured result
        return self._parse_response(response)
    
    def _build_prompt(self, metrics: Dict[str, Any], goal: str) -> str:
        """Build a prompt for the AI"""
        prompt = f"""You are a DevOps monitoring assistant. Analyze the following system metrics and recommend actions.

Goal: {goal}

System Metrics:
{json.dumps(metrics, indent=2, default=str)}

Available Tools (use ONLY these exact names):
- get_cpu_metrics: Get CPU usage and frequency
- get_memory_metrics: Get RAM usage statistics  
- get_disk_metrics: Get disk usage information
- get_network_metrics: Get network I/O statistics
- get_process_metrics: Get top processes by CPU (parameters: {{"top_n": 5}})
- get_all_metrics: Get all system metrics at once
- detect_anomalies: Detect abnormal spikes in metrics

Based on these metrics, determine:
1. What action should be taken?
2. Why is this action needed?
3. What tool should be used next? (MUST be one of the available tools above)
4. Is the goal complete?

Respond ONLY in JSON format:
{{
    "action": "Brief action description",
    "reasoning": "Detailed explanation",
    "tool_to_use": "get_all_metrics",
    "parameters": {{}},
    "confidence": 0.8,
    "is_complete": false
}}
"""
        return prompt
    
    def suggest_fix(self, anomaly_type: str, current_value: float, threshold: float) -> List[str]:
        """
        Suggest fixes for detected anomalies.
        
        Args:
            anomaly_type: Type of anomaly (cpu, memory, disk)
            current_value: Current metric value
            threshold: Threshold that was exceeded
        
        Returns:
            List of suggested fixes
        """
        suggestions = []
        
        if anomaly_type == "cpu":
            suggestions = [
                "Identify and terminate high-CPU processes",
                "Check for runaway applications or infinite loops",
                "Consider scaling up CPU resources",
                "Review scheduled tasks and cron jobs"
            ]
        elif anomaly_type == "memory":
            suggestions = [
                "Restart memory-intensive applications",
                "Check for memory leaks in applications",
                "Clear system cache: echo 3 > /proc/sys/vm/drop_caches",
                "Consider adding more RAM or swap space"
            ]
        elif anomaly_type == "disk":
            suggestions = [
                "Clean up temporary files and logs",
                "Remove unused packages and old kernels",
                "Archive or delete old data",
                "Consider adding more storage"
            ]
        else:
            suggestions = [
                "Investigate the anomaly further",
                "Check system logs for errors",
                "Monitor the trend over time"
            ]
        
        return suggestions


# Convenience function
def get_reasoner(mode: str = "mock", api_token: Optional[str] = None, ollama_url: str = "http://localhost:11434") -> MistralReasoner:
    """
    Get a configured MistralReasoner instance.
    
    Args:
        mode: "ollama", "local", "api", or "mock"
        api_token: HuggingFace API token (for API mode)
        ollama_url: Ollama API URL (for Ollama mode)
    
    Returns:
        Configured MistralReasoner
    """
    mode_enum = ReasoningMode(mode.lower())
    return MistralReasoner(mode=mode_enum, api_token=api_token, ollama_url=ollama_url)


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("DevOps Monitoring Agent - Reasoning Demo")
    print("=" * 60)
    
    # Test with mock mode (no AI required)
    reasoner = MistralReasoner(mode=ReasoningMode.MOCK)
    
    # Test case 1: High CPU
    print("\n1. High CPU Scenario:")
    metrics = {
        "cpu": {"percent": 85, "status": "warning"},
        "memory": {"percent": 60, "status": "normal"}
    }
    result = reasoner.analyze_metrics(metrics, "Check system health")
    print(f"   Action: {result.action}")
    print(f"   Tool: {result.tool_to_use}")
    print(f"   Confidence: {result.confidence}")
    
    # Test case 2: Normal system
    print("\n2. Normal System Scenario:")
    metrics = {
        "cpu": {"percent": 30, "status": "normal"},
        "memory": {"percent": 45, "status": "normal"}
    }
    result = reasoner.analyze_metrics(metrics, "Check system health")
    print(f"   Action: {result.action}")
    print(f"   Complete: {result.is_complete}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
