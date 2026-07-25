from typing import Dict, Any, List

class MCPAdapter:
    """Adapts internal AI tools to standard Model Context Protocol (MCP) JSON schemas."""

    @staticmethod
    def to_mcp_tool_schema(tool_name: str, description: str, input_schema: dict) -> dict:
        return {
            "name": tool_name,
            "description": description,
            "inputSchema": input_schema or {"type": "object", "properties": {}}
        }

    @staticmethod
    def format_mcp_response(result: Any, is_error: bool = False) -> dict:
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(result)
                }
            ],
            "isError": is_error
        }
