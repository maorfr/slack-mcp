import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("slack")

SLACK_API_BASE = "https://slack.com/api"


async def make_request(
    url: str, payload: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    xoxc_token = os.environ["SLACK_XOXC_TOKEN"]
    xoxd_token = os.environ["SLACK_XOXD_TOKEN"]

    headers = {
        "Authorization": f"Bearer {xoxc_token}",
        "Content-Type": "application/json",
    }

    cookies = {"d": xoxd_token}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url, headers=headers, cookies=cookies, json=payload, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)
            return None


@mcp.tool()
async def list_channels() -> str:
    """List all channels in the Slack workspace."""
    url = f"{SLACK_API_BASE}/conversations.list"
    data = await make_request(url)
    print(data)
    if data and data.get("ok"):
        return data.get("channels", [])


@mcp.tool()
async def get_channel_history(channel_id: str) -> str:
    """Get the history of a channel."""
    url = f"{SLACK_API_BASE}/conversations.history"
    payload = {"channel": channel_id}
    data = await make_request(url, payload=payload)
    print(data)
    if data and data.get("ok"):
        return data.get("messages", [])


@mcp.tool()
async def post_message(channel_id: str, message: str, thread_ts: str = "") -> str:
    """Post a message to a channel."""
    url = f"{SLACK_API_BASE}/chat.postMessage"
    payload = {"channel": channel_id, "text": message}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    data = await make_request(url, payload=payload)
    print(data)
    return data.get("ok")


@mcp.tool()
async def add_reaction(channel_id: str, message_ts: str, reaction: str) -> str:
    """Add a reaction to a message."""
    url = f"{SLACK_API_BASE}/reactions.add"
    payload = {"channel": channel_id, "name": reaction, "timestamp": message_ts}
    data = await make_request(url, payload=payload)
    print(data)
    return data.get("ok")


if __name__ == "__main__":
    mcp.run(transport="stdio")
