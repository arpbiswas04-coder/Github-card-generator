import os
import sys
from google.adk.agents import llm_agent
from google.adk.tools.mcp_tool import mcp_toolset
from dotenv import load_dotenv

load_dotenv()

# Define connection to the local MCP server
mcp_server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")

connection_params = mcp_toolset.StdioServerParameters(
    command=sys.executable, # Use the current python interpreter
    args=[mcp_server_path],
    env={**os.environ, "PYTHONPATH": os.path.dirname(__file__)}
)

# Create the MCP Toolset
mcp_tools = mcp_toolset.McpToolset(connection_params=connection_params)

# Define the Agent
github_card_agent = llm_agent.LlmAgent(
    name="github_card_agent",
    model="gemini-2.0-flash", # Switch back to 2.0
    instruction=(
        "You are a GitHub profile analyst and dev card generator. "
        "When a user gives you a GitHub username, you ALWAYS follow this exact sequence: "
        "first call scrape_github, then analyze_profile with the result, "
        "then generate_card_html with all three inputs, then save_card. "
        "Never skip steps. Be enthusiastic about developers' work. "
        "If the profile is private or doesn't exist, say so clearly."
    ),
    tools=[mcp_tools]
)
