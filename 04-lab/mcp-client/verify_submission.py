"""End-to-end checks for the Day 26 Weather MCP submission."""

import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


load_dotenv(Path(__file__).parents[2] / ".env")
SERVER_URL = "http://localhost:8085/mcp"
TOKEN = os.getenv("MCP_AUTH_TOKEN", "dev-token-abc123")


async def call_with_token() -> None:
    print("Checking valid token and legacy client...")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {TOKEN}"}) as client:
        async with streamable_http_client(SERVER_URL, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = {tool.name for tool in (await session.list_tools()).tools}
                assert {"get_current_weather", "get_current_weather_v2", "get_forecast", "health_check"} <= tools

                legacy = await session.call_tool("get_current_weather", {"city": "Hanoi"})
                assert legacy.content[0].text

                print("Checking server metadata and v2 client...")
                info = json.loads((await session.read_resource("server://info")).contents[0].text)
                assert info["version"] == "2.0.0"

                current = await session.call_tool("get_current_weather_v2", {"city": "Hanoi"})
                payload = json.loads(current.content[0].text)
                assert payload["api_version"] == "2.0" and "temperature_c" in payload
                print("✅ Valid token, legacy client, v2 client, and server://info passed")


async def rejects_missing_or_invalid_token(token: str | None) -> None:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "verify", "version": "1.0"}},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(SERVER_URL, headers=headers, json=request)
    assert response.status_code in {401, 403}, response.status_code


async def main() -> None:
    await call_with_token()
    print("Checking missing token...")
    await rejects_missing_or_invalid_token(None)
    print("Checking invalid token...")
    await rejects_missing_or_invalid_token("invalid-token")
    print("✅ Missing and invalid tokens were rejected")


if __name__ == "__main__":
    asyncio.run(main())
