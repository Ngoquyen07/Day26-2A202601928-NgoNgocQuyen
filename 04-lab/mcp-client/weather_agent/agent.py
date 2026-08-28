"""Weather Agent - connects to the authenticated local Weather MCP Server."""
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8085/mcp"
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "dev-token-abc123")

logger.info("🌐 Initializing weather agent with local MCP server")
logger.info(f"📡 MCP Server: {MCP_SERVER_URL}")

connection_params = StreamableHTTPConnectionParams(
    url=MCP_SERVER_URL,
    headers={"Authorization": f"Bearer {MCP_AUTH_TOKEN}"},
    timeout=30.0,
)
logger.info("🔌 Connecting to MCP server...")
weather_tools = McpToolset(connection_params=connection_params)
root_agent = Agent(name="weather_agent", model="gemini-3.6-flash", tools=[weather_tools])
logger.info("✅ Weather agent initialized with authenticated MCP tools")

