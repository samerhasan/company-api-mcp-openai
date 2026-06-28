"""Small MCP smoke test: lists tools exposed by the MCP server."""
import asyncio
import os

from dotenv import load_dotenv
from agents.mcp import MCPServerStreamableHttp

load_dotenv()

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")


async def main() -> None:
    async with MCPServerStreamableHttp(
        name="company-api-mcp",
        params={"url": MCP_URL, "timeout": 15},
        cache_tools_list=False,
    ) as server:
        tools = await server.list_tools()
        print("MCP tools found:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
