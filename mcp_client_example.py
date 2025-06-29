#!/usr/bin/env python3
"""
Example MCP client to test the server
"""

import json
import urllib.request
import urllib.parse

class MCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.request_id = 0
    
    def _make_request(self, method: str, params: dict = None):
        """Make a JSON-RPC request to the MCP server"""
        self.request_id += 1
        
        request_data = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        data = json.dumps(request_data).encode('utf-8')
        req = urllib.request.Request(
            self.server_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('result', result)
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def initialize(self):
        """Initialize the MCP connection"""
        return self._make_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
    
    def list_tools(self):
        """List available tools"""
        return self._make_request("tools/list")
    
    def call_tool(self, name: str, arguments: dict):
        """Call a specific tool"""
        return self._make_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
    
    def list_resources(self):
        """List available resources"""
        return self._make_request("resources/list")
    
    def read_resource(self, uri: str):
        """Read a specific resource"""
        return self._make_request("resources/read", {"uri": uri})
    
    def list_prompts(self):
        """List available prompts"""
        return self._make_request("prompts/list")
    
    def get_prompt(self, name: str, arguments: dict = None):
        """Get a specific prompt"""
        return self._make_request("prompts/get", {
            "name": name,
            "arguments": arguments or {}
        })

def main():
    """Test the MCP server"""
    client = MCPClient()
    
    print("=== MCP Client Test ===\n")
    
    # Initialize
    print("1. Initializing...")
    init_result = client.initialize()
    print(json.dumps(init_result, indent=2))
    print()
    
    # List tools
    print("2. Listing tools...")
    tools = client.list_tools()
    print(json.dumps(tools, indent=2))
    print()
    
    # Call schedule_call tool
    print("3. Calling schedule_call tool...")
    call_result = client.call_tool("schedule_call", {
        "candidate_name": "John Doe",
        "candidate_email": "john.doe@example.com",
        "candidate_phone": "+1234567890"
    })
    print(json.dumps(call_result, indent=2))
    print()
    
    # List resources
    print("4. Listing resources...")
    resources = client.list_resources()
    print(json.dumps(resources, indent=2))
    print()
    
    # Read knowledge base
    print("5. Reading knowledge base...")
    kb_data = client.read_resource("knowledge://base")
    print(json.dumps(kb_data, indent=2))
    print()
    
    # List prompts
    print("6. Listing prompts...")
    prompts = client.list_prompts()
    print(json.dumps(prompts, indent=2))
    print()
    
    # Get screening prompt
    print("7. Getting candidate screening prompt...")
    prompt = client.get_prompt("candidate_screening", {
        "candidate_background": "5 years Python development",
        "position": "Senior Software Engineer"
    })
    print(json.dumps(prompt, indent=2))

if __name__ == "__main__":
    main()