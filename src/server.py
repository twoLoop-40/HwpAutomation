"""MCP server for HWP automation."""

import asyncio
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .tools import TOOLS, ToolHandler


# Create server instance
app = Server("hwp-mcp-server")
tool_handler = ToolHandler()


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available HWP automation tools."""
    return TOOLS


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    return tool_handler.handle_call(name, arguments)


async def main():
    """Run the MCP server using stdio transport."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        initialization_options = InitializationOptions(
            server_name="hwp-mcp-server",
            server_version="0.1.0",
            capabilities=app.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )

        await app.run(
            read_stream,
            write_stream,
            initialization_options,
        )


def run_server():
    """Entry point for running the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n서버를 종료합니다...")
    finally:
        tool_handler.cleanup()


if __name__ == "__main__":
    run_server()
