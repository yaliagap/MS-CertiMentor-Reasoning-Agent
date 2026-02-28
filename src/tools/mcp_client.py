"""
Microsoft Learn MCP Client
Connects to Microsoft Learn MCP Server for retrieving learning content.
"""
import os
import asyncio
import httpx
from typing import Dict, List, Any, Optional
import json


class MicrosoftLearnMCPClient:
    """
    Client for Microsoft Learn MCP Server.

    Endpoint: https://learn.microsoft.com/api/mcp
    Protocol: MCP (Model Context Protocol) over HTTP

    Available tools:
    - microsoft_docs_search: Search Microsoft Learn documentation
    - microsoft_docs_fetch: Fetch specific content
    - microsoft_code_sample_search: Search code samples
    """

    def __init__(self, endpoint: str = None, timeout: int = 30):
        """
        Initialize MCP client.

        Args:
            endpoint: MCP server endpoint (default: from env or Microsoft Learn)
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint or os.getenv(
            "MCP_ENDPOINT",
            "https://learn.microsoft.com/api/mcp"
        )
        self.timeout = timeout
        self.session_id = None

    async def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP tool on the server.

        Args:
            tool_name: Name of the MCP tool to call
            arguments: Tool arguments

        Returns:
            Tool response as dictionary

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # MCP protocol request format
            request_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            try:
                response = await client.post(
                    self.endpoint,
                    json=request_payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                )
                response.raise_for_status()

                # Parse SSE format response
                # MCP server returns: "event: message\ndata: <JSON>\n\n"
                response_text = response.text.strip()

                # Extract JSON from SSE data field
                if response_text.startswith("event:"):
                    lines = response_text.split("\n")
                    for line in lines:
                        if line.startswith("data: "):
                            json_str = line[6:]  # Remove "data: " prefix
                            result = json.loads(json_str)
                            break
                    else:
                        # Fallback: try to parse as JSON directly
                        result = response.json()
                else:
                    # Not SSE format, parse as regular JSON
                    result = response.json()

                # Extract result from MCP response
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
                else:
                    return result

            except httpx.HTTPError as e:
                print(f"[MCP Client] HTTP Error: {e}")
                raise
            except Exception as e:
                print(f"[MCP Client] Error calling {tool_name}: {e}")
                raise

    async def search_docs(
        self,
        query: str,
        max_results: int = 10,
        content_type: str = "learning-path"
    ) -> List[Dict[str, Any]]:
        """
        Search Microsoft Learn documentation.

        Args:
            query: Search query
            max_results: Maximum number of results
            content_type: Type of content (e.g., "learning-path", "module", "certification")

        Returns:
            List of search results with title, URL, description, etc.
        """
        try:
            result = await self._call_mcp_tool(
                "microsoft_docs_search",
                {
                    "query": query,
                    "max_results": max_results,
                    "content_type": content_type
                }
            )

            # MCP server returns results in nested format:
            # {"content": [{"type": "text", "text": "{\"results\":[...]}"}]}
            if "content" in result and len(result["content"]) > 0:
                content_item = result["content"][0]
                if "text" in content_item:
                    # Parse the JSON string inside text field
                    import json as json_module
                    data = json_module.loads(content_item["text"])
                    return data.get("results", [])

            # Fallback: try direct access
            return result.get("results", [])
        except Exception as e:
            print(f"[MCP Client] Search failed: {e}")
            # Return empty list if search fails
            return []

    async def fetch_content(
        self,
        url: str
    ) -> Dict[str, Any]:
        """
        Fetch specific content from Microsoft Learn.

        Args:
            url: URL of the content to fetch

        Returns:
            Content details including title, description, modules, etc.
        """
        try:
            result = await self._call_mcp_tool(
                "microsoft_docs_fetch",
                {"url": url}
            )
            return result
        except Exception as e:
            print(f"[MCP Client] Fetch failed: {e}")
            return {}

    async def search_code_samples(
        self,
        query: str,
        language: str = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Microsoft Learn code samples.

        Args:
            query: Search query
            language: Programming language filter (optional)
            max_results: Maximum number of results

        Returns:
            List of code samples
        """
        try:
            arguments = {
                "query": query,
                "max_results": max_results
            }
            if language:
                arguments["language"] = language

            result = await self._call_mcp_tool(
                "microsoft_code_sample_search",
                arguments
            )
            return result.get("samples", [])
        except Exception as e:
            print(f"[MCP Client] Code sample search failed: {e}")
            return []


# Singleton instance
_mcp_client: Optional[MicrosoftLearnMCPClient] = None


def get_mcp_client() -> MicrosoftLearnMCPClient:
    """
    Get or create singleton MCP client instance.

    Returns:
        MicrosoftLearnMCPClient instance
    """
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MicrosoftLearnMCPClient()
    return _mcp_client
