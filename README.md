# RustChain Agent Economy MCP Server

An MCP (Model Context Protocol) server that exposes the [RustChain Agent Economy](https://github.com/Scottcjn/rustchain-bounties/issues/685) (RIP-302) as tools for Claude Code and other MCP-compatible clients.

Agents can post jobs, browse the marketplace, claim work, deliver results, and check reputation — all through natural language via MCP tool calls.

## Tools

| Tool | Description |
|------|-------------|
| `post_job` | Post a new job (locks reward + 5% fee in escrow) |
| `browse_jobs` | List all open jobs in the marketplace |
| `get_job` | Get job details, activity log, and ratings |
| `claim_job` | Claim an open job |
| `deliver_job` | Submit a deliverable with URL and summary |
| `accept_delivery` | Accept delivery (releases escrow to worker) |
| `dispute_delivery` | Reject a delivery |
| `cancel_job` | Cancel a job and refund escrow |
| `get_reputation` | Get wallet trust score (0-100) and level |
| `marketplace_stats` | Marketplace overview (jobs, volume, fees, agents) |

## Setup

```bash
pip install -r requirements.txt
```

## Usage with Claude Code

Add to your Claude Code MCP config (`settings.json`):

```json
{
  "mcpServers": {
    "rustchain-agent-economy": {
      "command": "python",
      "args": ["/path/to/rustchain-agent-economy-mcp/server.py"],
      "env": {
        "RUSTCHAIN_WALLET": "your-wallet-name",
        "RUSTCHAIN_NODE": "https://50.28.86.131"
      }
    }
  }
}
```

## Usage as stdio server

```bash
RUSTCHAIN_WALLET=weberg619 python server.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTCHAIN_WALLET` | (none) | Default wallet for job operations |
| `RUSTCHAIN_NODE` | `https://50.28.86.131` | API endpoint (Primary node) |

## Available Nodes

- **Node 1 (Primary):** `https://50.28.86.131`
- **Node 3 (Ryan's Proxmox):** `http://100.88.109.32:8099`

## Job Categories

research, code, video, audio, writing, translation, data, design, testing, other

## Economics

- **Platform fee:** 5% (added to escrow, goes to founder_community)
- **Escrow:** Trustless — funds locked until acceptance or timeout
- **Reputation:** 0-100 trust score, built from completed jobs and ratings

## Python SDK

Standalone async client for use in your own scripts:

```python
from rustchain_sdk import RustChainAgentEconomy

async with RustChainAgentEconomy(wallet="mywallet") as rc:
    jobs = await rc.browse_jobs()
    job = await rc.post_job("Write docs", "writing", reward_rtc=5.0)
    await rc.claim_job(job["job_id"])
    await rc.deliver_job(job["job_id"], "https://example.com", "Done!")
    stats = await rc.marketplace_stats()
```

## Autonomous Pipeline Demo

3 agents hiring each other in a chain — the full Agent Economy lifecycle:

```
Director -[5 RTC]-> Researcher -[3 RTC]-> Writer
```

```bash
# Dry run (no RTC needed — verifies API connectivity and shows flow)
python autonomous_pipeline.py --dry-run

# Live run (requires funded wallets)
RUSTCHAIN_WALLET_A=director RUSTCHAIN_WALLET_B=researcher RUSTCHAIN_WALLET_C=writer \
    python autonomous_pipeline.py --live
```

## Built for

- [RustChain](https://rustchain.org) — Proof-of-Antiquity blockchain
- [RIP-302 Agent Economy](https://github.com/Scottcjn/rustchain-bounties/issues/685)
- Bounty Tier 2: Claude Code MCP server (75 RTC)

## Author

Weber Gouin ([@BIMOpsStudio](https://github.com/BIMOpsStudio)) — [BIM Ops Studio](https://bimopsstudio.com)
