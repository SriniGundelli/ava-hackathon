# MCP Server for Ava AI Talent Assistant

This directory contains a basic Model Context Protocol (MCP) server implementation for the Ava AI Talent Assistant project, built using only Python standard library modules.

## Features

The MCP server provides the following capabilities:

### Tools
- **schedule_call**: Schedule calls with candidates using Cal.com integration
- **get_call_logs**: Retrieve call logs from the system
- **setup_twilio**: Setup Twilio SIP trunk and phone number

### Resources
- **knowledge_base**: Company knowledge base for candidate questions
- **call_transcripts**: Transcripts from voice calls with candidates
- **booking_data**: Scheduled call booking information

### Prompts
- **candidate_screening**: Prompt for screening candidates during voice calls
- **call_summary**: Generate summaries of candidate calls

## Usage

### Starting the Server

```bash
python3 mcp_server.py
```

The server will start on `http://localhost:8080` by default.

### Testing the Server

Use the included test client:

```bash
python3 mcp_client_example.py
```

### Manual Testing with curl

Initialize the connection:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }'
```

List available tools:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

Call the schedule_call tool:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "schedule_call",
      "arguments": {
        "candidate_name": "John Doe",
        "candidate_email": "john.doe@example.com",
        "candidate_phone": "+1234567890"
      }
    }
  }'
```

## Integration with ElevenLabs

To integrate this MCP server with your ElevenLabs agent:

1. Start the MCP server: `python3 mcp_server.py`
2. Configure your ElevenLabs agent to use the MCP server endpoint
3. The agent can now call the available tools, access resources, and use prompts

## Limitations

Due to WebContainer environment constraints:
- Uses only Python standard library (no pip packages)
- Simulates external API calls (actual integration would require the real APIs)
- Basic HTTP server implementation (production would use proper ASGI/WSGI server)

## Extending the Server

To add new tools, resources, or prompts:

1. Add the definition to the appropriate `_setup_default_*` method
2. Implement the handler method (e.g., `_handle_new_tool`)
3. Add the routing logic in the main handler methods

## Files

- `mcp_server.py`: Main MCP server implementation
- `mcp_client_example.py`: Example client for testing
- `README_MCP.md`: This documentation file