"""
Web search mock tool for MCP server.
"""

from typing import Any, Dict
import random


class WebSearchTool:
    """Mock web search tool for demonstration."""
    
    name = "web_search"
    description = "Search the web for information (mock implementation)"
    
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 5
            }
        },
        "required": ["query"]
    }
    
    # Mock search results database
    MOCK_RESULTS = {
        "python": [
            {"title": "Python Programming Language", "url": "https://python.org", "snippet": "Python is a high-level programming language."},
            {"title": "Python Tutorial - W3Schools", "url": "https://w3schools.com/python", "snippet": "Learn Python with our tutorial."},
        ],
        "machine learning": [
            {"title": "Machine Learning - Wikipedia", "url": "https://en.wikipedia.org/wiki/Machine_learning", "snippet": "Machine learning is a subset of AI."},
            {"title": "What is Machine Learning?", "url": "https://ibm.com/topics/machine-learning", "snippet": "Machine learning enables computers to learn from data."},
        ],
        "docker": [
            {"title": "Docker Documentation", "url": "https://docs.docker.com", "snippet": "Docker is a platform for developing applications."},
            {"title": "What is Docker?", "url": "https://docker.com/what-is-docker", "snippet": "Docker helps developers build, share, and run applications."},
        ],
        "fastapi": [
            {"title": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com", "snippet": "FastAPI is a modern web framework for Python."},
            {"title": "FastAPI GitHub", "url": "https://github.com/tiangolo/fastapi", "snippet": "FastAPI framework, high performance."},
        ],
        "mcp": [
            {"title": "Model Context Protocol", "url": "https://modelcontextprotocol.io", "snippet": "MCP is an open protocol for AI tool integration."},
            {"title": "MCP Specification", "url": "https://spec.modelcontextprotocol.io", "snippet": "The official MCP specification."},
        ],
    }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search."""
        query = arguments.get("query", "").lower()
        num_results = min(arguments.get("num_results", 5), 10)
        
        if not query:
            return {
                "content": [{"type": "text", "text": "Error: Empty query"}],
                "isError": True
            }
        
        # Find matching results
        results = []
        for keyword, items in self.MOCK_RESULTS.items():
            if keyword in query or query in keyword:
                results.extend(items)
        
        # If no specific matches, return generic results
        if not results:
            results = [
                {"title": f"Search results for '{query}'", "url": f"https://example.com/search?q={query}", "snippet": f"This is a mock search result for '{query}'."},
                {"title": f"More about {query}", "url": f"https://example.com/{query}", "snippet": f"Additional information about {query}."},
            ]
        
        # Limit results
        results = results[:num_results]
        
        # Format output
        output = f"Search results for: '{query}'\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['title']}\n"
            output += f"   URL: {result['url']}\n"
            output += f"   {result['snippet']}\n\n"
        
        return {
            "content": [{"type": "text", "text": output}],
            "isError": False
        }


# Tool instance
web_search_tool = WebSearchTool()
