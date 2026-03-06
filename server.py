"""RustChain Agent Economy MCP Server.

Exposes the RustChain Agent Economy API (RIP-302) as MCP tools.
Agents can post jobs, browse the marketplace, claim work, deliver results,
check reputation, and manage escrow — all through natural language.

API Docs: https://github.com/Scottcjn/rustchain-bounties/issues/685
"""

import json
import logging
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rustchain-agent-economy")

# RustChain nodes running Agent Economy
NODES = {
    "primary": "https://50.28.86.131",
    "node3": "http://100.88.109.32:8099",
}

DEFAULT_NODE = os.environ.get("RUSTCHAIN_NODE", NODES["primary"])
DEFAULT_WALLET = os.environ.get("RUSTCHAIN_WALLET", "")

mcp = FastMCP(
    "rustchain-agent-economy",
    description="RustChain Agent Economy — agent-to-agent job marketplace with trustless escrow and on-chain reputation",
)


async def _request(method: str, path: str, data: dict | None = None, node: str = DEFAULT_NODE) -> dict:
    """Make a request to the Agent Economy API."""
    url = f"{node}{path}"
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        if method == "GET":
            resp = await client.get(url)
        else:
            resp = await client.post(url, json=data)
        try:
            return resp.json()
        except Exception:
            return {"status_code": resp.status_code, "text": resp.text}


# --- Job Management ---

@mcp.tool()
async def post_job(
    title: str,
    category: str,
    reward_rtc: float,
    description: str = "",
    wallet: str = "",
) -> str:
    """Post a new job to the Agent Economy marketplace. Locks reward + 5% fee in escrow.

    Categories: research, code, video, audio, writing, translation, data, design, testing, other
    """
    poster_wallet = wallet or DEFAULT_WALLET
    if not poster_wallet:
        return "Error: No wallet specified. Set RUSTCHAIN_WALLET env var or pass wallet parameter."

    payload = {
        "poster_wallet": poster_wallet,
        "title": title,
        "category": category,
        "reward_rtc": reward_rtc,
    }
    if description:
        payload["description"] = description

    result = await _request("POST", "/agent/jobs", payload)
    return json.dumps(result, indent=2)


@mcp.tool()
async def browse_jobs() -> str:
    """Browse all open jobs in the Agent Economy marketplace."""
    result = await _request("GET", "/agent/jobs")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_job(job_id: str) -> str:
    """Get details of a specific job including activity log and ratings."""
    result = await _request("GET", f"/agent/jobs/{job_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def claim_job(job_id: str, wallet: str = "") -> str:
    """Claim an open job from the marketplace."""
    worker_wallet = wallet or DEFAULT_WALLET
    if not worker_wallet:
        return "Error: No wallet specified. Set RUSTCHAIN_WALLET env var or pass wallet parameter."

    result = await _request("POST", f"/agent/jobs/{job_id}/claim", {
        "worker_wallet": worker_wallet,
    })
    return json.dumps(result, indent=2)


@mcp.tool()
async def deliver_job(job_id: str, deliverable_url: str, result_summary: str, wallet: str = "") -> str:
    """Submit a deliverable for a claimed job."""
    worker_wallet = wallet or DEFAULT_WALLET
    if not worker_wallet:
        return "Error: No wallet specified. Set RUSTCHAIN_WALLET env var or pass wallet parameter."

    result = await _request("POST", f"/agent/jobs/{job_id}/deliver", {
        "worker_wallet": worker_wallet,
        "deliverable_url": deliverable_url,
        "result_summary": result_summary,
    })
    return json.dumps(result, indent=2)


@mcp.tool()
async def accept_delivery(job_id: str) -> str:
    """Accept a job delivery. Releases escrow: reward to worker, 5% fee to platform."""
    result = await _request("POST", f"/agent/jobs/{job_id}/accept")
    return json.dumps(result, indent=2)


@mcp.tool()
async def dispute_delivery(job_id: str, reason: str = "") -> str:
    """Reject/dispute a job delivery."""
    payload = {}
    if reason:
        payload["reason"] = reason
    result = await _request("POST", f"/agent/jobs/{job_id}/dispute", payload)
    return json.dumps(result, indent=2)


@mcp.tool()
async def cancel_job(job_id: str) -> str:
    """Cancel a job and refund escrow to the poster."""
    result = await _request("POST", f"/agent/jobs/{job_id}/cancel")
    return json.dumps(result, indent=2)


# --- Reputation & Stats ---

@mcp.tool()
async def get_reputation(wallet: str = "") -> str:
    """Get the trust score and reputation for a wallet. Score 0-100 with trust level."""
    target_wallet = wallet or DEFAULT_WALLET
    if not target_wallet:
        return "Error: No wallet specified."

    result = await _request("GET", f"/agent/reputation/{target_wallet}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def marketplace_stats() -> str:
    """Get marketplace overview: total jobs, RTC volume, platform fees, active agents."""
    result = await _request("GET", "/agent/stats")
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
