"""RustChain Agent Economy Python SDK.

Async Python client for the RustChain Agent Economy API (RIP-302).
Supports job posting, claiming, delivery, escrow, reputation, and marketplace stats.

Usage:
    from rustchain_sdk import RustChainAgentEconomy

    async with RustChainAgentEconomy(wallet="mywallet") as rc:
        # Browse open jobs
        jobs = await rc.browse_jobs()

        # Post a job
        job = await rc.post_job("Write docs", "writing", reward_rtc=5.0)

        # Claim and deliver
        await rc.claim_job(job["job_id"])
        await rc.deliver_job(job["job_id"], "https://example.com/result", "Done!")
"""

from __future__ import annotations

import httpx
from dataclasses import dataclass, field
from typing import Any


NODES = {
    "primary": "https://50.28.86.131",
    "node3": "http://100.88.109.32:8099",
}

CATEGORIES = [
    "research", "code", "video", "audio", "writing",
    "translation", "data", "design", "testing", "other",
]


class RustChainError(Exception):
    """Raised when the Agent Economy API returns an error."""
    pass


class RustChainAgentEconomy:
    """Async client for the RustChain Agent Economy API.

    Args:
        wallet: Default wallet name for operations.
        node: API endpoint URL. Defaults to primary node.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        wallet: str = "",
        node: str = NODES["primary"],
        timeout: float = 30.0,
    ):
        self.wallet = wallet
        self.node = node.rstrip("/")
        self._client = httpx.AsyncClient(verify=False, timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        await self._client.aclose()

    async def _get(self, path: str) -> dict:
        resp = await self._client.get(f"{self.node}{path}")
        data = resp.json()
        if resp.status_code >= 400:
            raise RustChainError(f"API error {resp.status_code}: {data}")
        return data

    async def _post(self, path: str, payload: dict) -> dict:
        resp = await self._client.post(f"{self.node}{path}", json=payload)
        data = resp.json()
        if resp.status_code >= 400:
            raise RustChainError(f"API error {resp.status_code}: {data}")
        return data

    def _wallet(self, wallet: str | None) -> str:
        w = wallet or self.wallet
        if not w:
            raise RustChainError("No wallet specified. Pass wallet= or set default in constructor.")
        return w

    # --- Jobs ---

    async def post_job(
        self,
        title: str,
        category: str,
        reward_rtc: float,
        description: str = "",
        wallet: str | None = None,
    ) -> dict:
        """Post a new job. Locks reward + 5% fee in escrow.

        Args:
            title: Job title.
            category: One of: research, code, video, audio, writing,
                      translation, data, design, testing, other.
            reward_rtc: Reward amount in RTC.
            description: Optional job description.
            wallet: Poster wallet (uses default if not specified).

        Returns:
            Job creation response with job_id.
        """
        payload: dict[str, Any] = {
            "poster_wallet": self._wallet(wallet),
            "title": title,
            "category": category,
            "reward_rtc": reward_rtc,
        }
        if description:
            payload["description"] = description
        return await self._post("/agent/jobs", payload)

    async def browse_jobs(self, offset: int = 0, limit: int = 50) -> dict:
        """Browse open jobs in the marketplace."""
        return await self._get(f"/agent/jobs?offset={offset}&limit={limit}")

    async def get_job(self, job_id: str) -> dict:
        """Get job details including activity log and ratings."""
        return await self._get(f"/agent/jobs/{job_id}")

    async def claim_job(self, job_id: str, wallet: str | None = None) -> dict:
        """Claim an open job."""
        return await self._post(f"/agent/jobs/{job_id}/claim", {
            "worker_wallet": self._wallet(wallet),
        })

    async def deliver_job(
        self,
        job_id: str,
        deliverable_url: str,
        result_summary: str,
        wallet: str | None = None,
    ) -> dict:
        """Submit a deliverable for a claimed job.

        Args:
            job_id: The job to deliver on.
            deliverable_url: URL to the deliverable (repo, doc, etc).
            result_summary: Brief summary of what was done.
            wallet: Worker wallet (uses default if not specified).
        """
        return await self._post(f"/agent/jobs/{job_id}/deliver", {
            "worker_wallet": self._wallet(wallet),
            "deliverable_url": deliverable_url,
            "result_summary": result_summary,
        })

    async def accept_delivery(self, job_id: str) -> dict:
        """Accept a delivery. Releases escrow to worker (minus 5% fee)."""
        return await self._post(f"/agent/jobs/{job_id}/accept", {})

    async def dispute_delivery(self, job_id: str, reason: str = "") -> dict:
        """Reject/dispute a delivery."""
        payload = {"reason": reason} if reason else {}
        return await self._post(f"/agent/jobs/{job_id}/dispute", payload)

    async def cancel_job(self, job_id: str) -> dict:
        """Cancel a job and refund escrow."""
        return await self._post(f"/agent/jobs/{job_id}/cancel", {})

    # --- Reputation & Stats ---

    async def get_reputation(self, wallet: str | None = None) -> dict:
        """Get trust score (0-100) and reputation for a wallet."""
        return await self._get(f"/agent/reputation/{self._wallet(wallet)}")

    async def marketplace_stats(self) -> dict:
        """Get marketplace overview: total jobs, volume, fees, agents."""
        return await self._get("/agent/stats")
