"""
Calculator tool for MCP server.
"""

import json
import re
from typing import Any, Dict


class CalculatorTool:
    """Safe calculator tool with expression evaluation."""
    
    name = "calculator"
    description = "Evaluate mathematical expressions safely"
    
    input_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g., '2 + 2 * 3')"
            }
        },
        "required": ["expression"]
    }
    
    # Allowed characters in expressions
    ALLOWED_CHARS = set("0123456789+-*/.()^ sqrtlogsin cos tanpi e ")
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calculator tool."""
        expression = arguments.get("expression", "")
        
        if not expression:
            return {
                "content": [{"type": "text", "text": "Error: Empty expression"}],
                "isError": True
            }
        
        # Security check
        if not self._is_safe(expression):
            return {
                "content": [{"type": "text", "text": "Error: Expression contains unsafe characters"}],
                "isError": True
            }
        
        try:
            result = self._evaluate(expression)
            return {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
    
    def _is_safe(self, expression: str) -> bool:
        """Check if expression is safe to evaluate."""
        # Check for dangerous patterns
        dangerous = ["__", "import", "exec", "eval", "compile", "open", "file", "os", "sys"]
        lower_expr = expression.lower()
        
        for pattern in dangerous:
            if pattern in lower_expr:
                return False
        
        # Check characters
        for char in expression:
            if char not in self.ALLOWED_CHARS:
                return False
        
        return True
    
    def _evaluate(self, expression: str) -> float:
        """Safely evaluate mathematical expression."""
        import math
        
        # Replace common math functions
        expression = expression.lower()
        expression = expression.replace("^", "**")
        expression = expression.replace("pi", str(3.14159265359))
        expression = expression.replace("e", str(2.71828182846))
        
        # Handle sqrt, log, sin, cos, tan - use math prefix directly
        expression = re.sub(r'sqrt\(([^)]+)\)', r'math.sqrt(\1)', expression)
        expression = re.sub(r'log\(([^)]+)\)', r'math.log(\1)', expression)
        expression = re.sub(r'sin\(([^)]+)\)', r'math.sin(\1)', expression)
        expression = re.sub(r'cos\(([^)]+)\)', r'math.cos(\1)', expression)
        expression = re.sub(r'tan\(([^)]+)\)', r'math.tan(\1)', expression)
        
        # Evaluate safely with math module available
        try:
            result = eval(expression, {"__builtins__": {}}, {"math": math})
            return round(result, 10)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")


# Tool instance
calculator_tool = CalculatorTool()
