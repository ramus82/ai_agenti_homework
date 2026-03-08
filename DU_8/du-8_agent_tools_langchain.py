import asyncio
import os
from dotenv import load_dotenv
#from langchain_core.tools import tool
#from langchain_openai import ChatOpenAI
#from langchain.agents import create_agent

"""
from langchain_mcp_adapters.client import MultiServerMCPClient
from visualizer import visualize
"""

load_dotenv()

# Model
#llm = ChatOpenAI(model="gpt-5-mini")


# ============================================================================
# MCP CLIENT SETUP
# ============================================================================


def get_tavily_mcp_url():
    """Get Tavily MCP URL with API key."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment")
    return f"https://mcp.tavily.com/mcp/?tavilyApiKey={api_key}"


async def get_mcp_tools():
    pass
    """Load tools from Tavily MCP server.
    client = MultiServerMCPClient(
        {
            "tavily": {
                "url": get_tavily_mcp_url(),
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    return tools, client
    """

#@tool
#def get_food() -> str:
#    """Get a plate of spaghetti."""
#    return "Here is your plate of spaghetti 🍝"


async def main():
    """Main async function to initialize and run the graph."""

    # Initialize MCP tools
    print("Initializing MCP connection to Tavily...")
    mcp_tools, mcp_client = await get_mcp_tools()
    print(f"Loaded {len(mcp_tools)} tools from Tavily MCP\n")

    # Combine all tools
    tools = list(mcp_tools) + [get_food]

    # Agent
    """Create an agent with the loaded tools and a simple system prompt.
    agent = create_agent(
        llm,
        tools=tools,
        system_prompt="You are a helpful assistant. Be concise and accurate.",
    )
    """

    # Visualize the graph
    #visualize(agent, "graph.png")

    # ---------------------------
    # Run the agent
    # MESSAGES are stored ONLY within the agent state !!!!
    # EACH USER INPUT IS A NEW STATE !!!!
    # =>  NO HISTORY for chat interaction !!!!!!
    # ---------------------------
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )
        print("Assistant:", result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())