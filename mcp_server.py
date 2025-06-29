#!/usr/bin/env python3
"""
Basic MCP Server for ElevenLabs Ava AI Talent Assistant
Uses only Python standard library modules due to WebContainer limitations
"""

import json
import sys
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List, Optional
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServer:
    """Basic MCP Server implementation"""
    
    def __init__(self):
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        self._setup_default_tools()
        self._setup_default_resources()
        self._setup_default_prompts()
    
    def _setup_default_tools(self):
        """Setup default tools for the ElevenLabs project"""
        self.tools = {
            "schedule_call": {
                "name": "schedule_call",
                "description": "Schedule a call with a candidate using Cal.com integration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "candidate_name": {"type": "string", "description": "Name of the candidate"},
                        "candidate_email": {"type": "string", "description": "Email of the candidate"},
                        "candidate_phone": {"type": "string", "description": "Phone number of the candidate"},
                        "time_zone": {"type": "string", "description": "Timezone for the call", "default": "America/New_York"}
                    },
                    "required": ["candidate_name", "candidate_email"]
                }
            },
            "get_call_logs": {
                "name": "get_call_logs",
                "description": "Retrieve call logs from the system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of logs to retrieve", "default": 10},
                        "call_sid": {"type": "string", "description": "Specific call SID to retrieve"}
                    }
                }
            },
            "setup_twilio": {
                "name": "setup_twilio",
                "description": "Setup Twilio SIP trunk and phone number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "friendly_name": {"type": "string", "description": "Friendly name for the setup"},
                        "elevenlabs_domain": {"type": "string", "description": "ElevenLabs domain for SIP"},
                        "voice_webhook_url": {"type": "string", "description": "Webhook URL for voice calls"}
                    },
                    "required": ["friendly_name", "elevenlabs_domain", "voice_webhook_url"]
                }
            }
        }
    
    def _setup_default_resources(self):
        """Setup default resources"""
        self.resources = {
            "knowledge_base": {
                "uri": "knowledge://base",
                "name": "Knowledge Base",
                "description": "Company knowledge base for candidate questions",
                "mimeType": "application/json"
            },
            "call_transcripts": {
                "uri": "transcripts://calls",
                "name": "Call Transcripts",
                "description": "Transcripts from voice calls with candidates",
                "mimeType": "text/plain"
            },
            "booking_data": {
                "uri": "bookings://data",
                "name": "Booking Data",
                "description": "Scheduled call booking information",
                "mimeType": "application/json"
            }
        }
    
    def _setup_default_prompts(self):
        """Setup default prompts"""
        self.prompts = {
            "candidate_screening": {
                "name": "candidate_screening",
                "description": "Prompt for screening candidates during voice calls",
                "arguments": [
                    {
                        "name": "candidate_background",
                        "description": "Background information about the candidate",
                        "required": False
                    },
                    {
                        "name": "position",
                        "description": "Position the candidate is applying for",
                        "required": False
                    }
                ]
            },
            "call_summary": {
                "name": "call_summary",
                "description": "Generate a summary of a candidate call",
                "arguments": [
                    {
                        "name": "transcript",
                        "description": "Call transcript to summarize",
                        "required": True
                    }
                ]
            }
        }
    
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "prompts": {"listChanged": True}
            },
            "serverInfo": {
                "name": "ava-mcp-server",
                "version": "1.0.0",
                "description": "MCP Server for Ava AI Talent Assistant"
            }
        }
    
    def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": list(self.tools.values())
        }
    
    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Tool '{tool_name}' not found"}]
            }
        
        # Simulate tool execution
        if tool_name == "schedule_call":
            return self._handle_schedule_call(arguments)
        elif tool_name == "get_call_logs":
            return self._handle_get_call_logs(arguments)
        elif tool_name == "setup_twilio":
            return self._handle_setup_twilio(arguments)
        
        return {
            "content": [{"type": "text", "text": f"Tool '{tool_name}' executed successfully"}]
        }
    
    def _handle_schedule_call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schedule_call tool execution"""
        candidate_name = arguments.get("candidate_name")
        candidate_email = arguments.get("candidate_email")
        
        if not candidate_name or not candidate_email:
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Missing required fields: candidate_name and candidate_email"}]
            }
        
        # Simulate successful scheduling
        result = {
            "success": True,
            "booking": {
                "candidate_name": candidate_name,
                "candidate_email": candidate_email,
                "scheduled_time": "2024-01-15T10:00:00Z",
                "meeting_url": "https://cal.com/meeting/abc123",
                "booking_uid": "booking_123456"
            }
        }
        
        return {
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
        }
    
    def _handle_get_call_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_call_logs tool execution"""
        limit = arguments.get("limit", 10)
        call_sid = arguments.get("call_sid")
        
        # Simulate call logs data
        logs = [
            {
                "id": 1,
                "call_sid": "CA123456789",
                "from_number": "+1234567890",
                "to_number": "+447883320201",
                "call_status": "completed",
                "created_at": "2024-01-15T09:30:00Z"
            },
            {
                "id": 2,
                "call_sid": "CA987654321",
                "from_number": "+1987654321",
                "to_number": "+447883320201",
                "call_status": "completed",
                "created_at": "2024-01-15T08:15:00Z"
            }
        ]
        
        if call_sid:
            logs = [log for log in logs if log["call_sid"] == call_sid]
        
        return {
            "content": [{"type": "text", "text": json.dumps(logs[:limit], indent=2)}]
        }
    
    def _handle_setup_twilio(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle setup_twilio tool execution"""
        friendly_name = arguments.get("friendly_name")
        elevenlabs_domain = arguments.get("elevenlabs_domain")
        voice_webhook_url = arguments.get("voice_webhook_url")
        
        # Simulate successful setup
        result = {
            "success": True,
            "setup": {
                "trunkSid": "TK123456789",
                "phoneNumber": "+447883320201",
                "voiceWebhookUrl": voice_webhook_url,
                "elevenLabsSipUri": f"sip:{elevenlabs_domain}.sip.11.ai"
            }
        }
        
        return {
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
        }
    
    def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        return {
            "resources": list(self.resources.values())
        }
    
    def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        
        if uri == "knowledge://base":
            content = {
                "company_info": {
                    "name": "TechCorp",
                    "culture": "Innovation-driven, collaborative environment",
                    "perks": ["Remote work", "Health insurance", "Stock options"]
                },
                "job_openings": [
                    {"title": "Software Engineer", "department": "Engineering", "location": "Remote"},
                    {"title": "Product Manager", "department": "Product", "location": "San Francisco"}
                ]
            }
            return {
                "contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(content, indent=2)}]
            }
        
        return {
            "contents": [{"uri": uri, "mimeType": "text/plain", "text": "Resource not found"}]
        }
    
    def handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        return {
            "prompts": list(self.prompts.values())
        }
    
    def handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "candidate_screening":
            prompt_text = """You are Ava, an AI talent assistant. Your role is to:
1. Answer candidate questions about the company, culture, and job openings
2. Assess candidate fit and interest level
3. Schedule 15-minute screening calls when appropriate

Be conversational, helpful, and professional. Focus on understanding the candidate's background and motivations."""
            
            if arguments.get("candidate_background"):
                prompt_text += f"\n\nCandidate Background: {arguments['candidate_background']}"
            
            if arguments.get("position"):
                prompt_text += f"\nPosition: {arguments['position']}"
            
            return {
                "description": "Screening prompt for candidate calls",
                "messages": [{"role": "system", "content": {"type": "text", "text": prompt_text}}]
            }
        
        elif name == "call_summary":
            transcript = arguments.get("transcript", "")
            prompt_text = f"""Please provide a concise summary of this candidate call transcript:

{transcript}

Include:
- Key points discussed
- Candidate's background and interests
- Next steps or recommendations
- Overall assessment"""
            
            return {
                "description": "Call summary generation",
                "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}]
            }
        
        return {
            "description": "Prompt not found",
            "messages": [{"role": "system", "content": {"type": "text", "text": "Prompt not available"}}]
        }

class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server"""
    
    def __init__(self, mcp_server: MCPServer, *args, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            # Route the request to appropriate handler
            if method == "initialize":
                result = self.mcp_server.handle_initialize(params)
            elif method == "tools/list":
                result = self.mcp_server.handle_tools_list(params)
            elif method == "tools/call":
                result = self.mcp_server.handle_tools_call(params)
            elif method == "resources/list":
                result = self.mcp_server.handle_resources_list(params)
            elif method == "resources/read":
                result = self.mcp_server.handle_resources_read(params)
            elif method == "prompts/list":
                result = self.mcp_server.handle_prompts_list(params)
            elif method == "prompts/get":
                result = self.mcp_server.handle_prompts_get(params)
            else:
                result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}
            
            # Send response
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def create_handler(mcp_server):
    """Create a request handler with the MCP server instance"""
    def handler(*args, **kwargs):
        return MCPRequestHandler(mcp_server, *args, **kwargs)
    return handler

def main():
    """Main function to run the MCP server"""
    port = 8080
    mcp_server = MCPServer()
    
    handler = create_handler(mcp_server)
    httpd = HTTPServer(('localhost', port), handler)
    
    logger.info(f"MCP Server starting on http://localhost:{port}")
    logger.info("Available endpoints:")
    logger.info("  POST / - MCP JSON-RPC requests")
    logger.info("Available tools: " + ", ".join(mcp_server.tools.keys()))
    logger.info("Available resources: " + ", ".join(mcp_server.resources.keys()))
    logger.info("Available prompts: " + ", ".join(mcp_server.prompts.keys()))
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        httpd.shutdown()

if __name__ == "__main__":
    main()