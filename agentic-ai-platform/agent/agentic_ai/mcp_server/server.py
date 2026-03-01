#!/usr/bin/env python3
"""
MCP Server - Model Context Protocol implementation.

Supports both stdio and HTTP transports.
"""

import json
import sys
import asyncio
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from .registry import registry
from ..utils.config import config
from ..utils.logger import logger


class MCPRequestHandler:
    """Handles MCP JSON-RPC requests."""
    
    def __init__(self):
        self.request_count = 0
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a single MCP request."""
        method = request.get("method")
        request_id = request.get("id")
        
        self.request_count += 1
        
        if method == "initialize":
            return self._handle_initialize(request_id)
        
        elif method == "tools/list":
            return self._handle_list_tools(request_id)
        
        elif method == "tools/call":
            return self._handle_call_tool(request, request_id)
        
        else:
            return self._send_error(request_id, -32601, f"Method not found: {method}")
    
    def _handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                }
            },
            "id": request_id
        }
    
    def _handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools = registry.list_tools()
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": request_id
        }
    
    def _handle_call_tool(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle tools/call request."""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"MCP tool call: {tool_name}", tool_name=tool_name, arguments=arguments)
        
        result = registry.execute(tool_name, arguments)
        
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    def _send_error(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Send error response."""
        return {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": request_id
        }


class MCPStdioServer:
    """MCP Server using stdio transport."""
    
    def __init__(self):
        self.handler = MCPRequestHandler()
        self.running = False
    
    def run(self):
        """Run the stdio server."""
        self.running = True
        logger.info("MCP stdio server started")
        
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handler.handle(request)
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                    "id": None
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            
            except Exception as e:
                logger.error(f"Server error: {str(e)}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                    "id": None
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
        
        logger.info("MCP stdio server stopped")
    
    def stop(self):
        """Stop the server."""
        self.running = False


class MCPHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP."""
    
    handler = MCPRequestHandler()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            request = json.loads(body)
            response = self.handler.handle(request)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": None
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()


class MCPHTTPServer:
    """MCP Server using HTTP transport."""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or config.MCP_SERVER_HOST
        self.port = port or config.MCP_SERVER_PORT
        self.server = None
        self.thread = None
    
    def run(self):
        """Run the HTTP server."""
        self.server = HTTPServer((self.host, self.port), MCPHTTPRequestHandler)
        logger.info(f"MCP HTTP server started on {self.host}:{self.port}")
        
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            logger.info("MCP HTTP server stopped")


def run_server(transport: str = None):
    """Run MCP server with specified transport."""
    transport = transport or config.MCP_TRANSPORT
    
    if transport == "stdio":
        server = MCPStdioServer()
        server.run()
    elif transport == "http":
        server = MCPHTTPServer()
        server.run()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            server.stop()
    else:
        print(f"Unknown transport: {transport}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_server()
