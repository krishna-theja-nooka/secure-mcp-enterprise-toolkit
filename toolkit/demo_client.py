"""Real MCP client: initialize, discover schemas, call a read-only tool."""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demo():
    parameters = StdioServerParameters(
        command=sys.executable, args=["-m", "toolkit.mcp_server"], env=dict(os.environ)
    )
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Discovered tools:", ", ".join(tool.name for tool in tools.tools))
            result = await session.call_tool("fleet_analytics", {"region": "All"})
            print(json.dumps(result.structuredContent, indent=2))


if __name__ == "__main__":
    asyncio.run(demo())
