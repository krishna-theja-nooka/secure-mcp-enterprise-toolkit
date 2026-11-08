import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_real_mcp_transport(settings, tmp_path):
    path = tmp_path / "keys.json"
    path.write_text(json.dumps(settings.keys))

    async def check():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "toolkit.mcp_server"],
            env={
                **os.environ,
                "TOOLKIT_HOME": str(tmp_path),
                "TOOLKIT_KEYS_FILE": str(path),
                "TOOLKIT_API_KEY": "operator",
            },
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                discovered = await session.list_tools()
                assert {t.name for t in discovered.tools} == {
                    "fleet_analytics",
                    "document_lookup",
                    "propose_ticket",
                }
                assert all(t.outputSchema for t in discovered.tools)
                result = await session.call_tool("fleet_analytics", {"region": "Austin"})
                assert not result.isError
                assert result.structuredContent["status"] == "ok"
                assert result.structuredContent["data"]["rows"][0]["vehicles"] == 8
                denied = await session.call_tool(
                    "fleet_analytics", {"metric": "DROP TABLE vehicles"}
                )
                assert denied.isError
                pending = await session.call_tool(
                    "propose_ticket",
                    {
                        "vehicle_id": "EV-006",
                        "title": "Review vehicle alerts",
                        "description": "Inspect synthetic history before escalation.",
                    },
                )
                assert pending.structuredContent["data"]["status"] == "pending"

    asyncio.run(asyncio.wait_for(check(), timeout=30))
