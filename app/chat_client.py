import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession
from agents.mcp import MCPServerStreamableHttp

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")

SYSTEM_INSTRUCTIONS = """
You are a helpful company API assistant.
Use MCP tools whenever the user asks about customers, products, orders, or backend API status.
Do not invent customer IDs, product IDs, or order IDs. Look them up with tools first.
Before creating new records, summarize what you are about to create in plain language.
After a tool call, explain the result clearly and include the important IDs.
""".strip()


async def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env or your terminal environment.")

    print("Company API Chat Client")
    print("Type 'exit' to stop.")
    print("Example: list products")
    print("Example: find customer Samer and create an order for MCP Integration Package")
    print()

    session = SQLiteSession("local-demo-user", "chat_history.db")

    async with MCPServerStreamableHttp(
        name="company-api-mcp",
        params={"url": MCP_URL, "timeout": 15},
        cache_tools_list=True,
    ) as mcp_server:
        agent = Agent(
            name="Company API Assistant",
            model=OPENAI_MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            mcp_servers=[mcp_server],
            mcp_config={
                "convert_schemas_to_strict": True,
                "include_server_in_tool_names": True,
            },
        )

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit", "q"}:
                print("Bye.")
                return
            if not user_input:
                continue

            result = await Runner.run(agent, user_input, session=session)
            print(f"Assistant: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(main())
