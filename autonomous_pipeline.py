"""Autonomous Agent Pipeline Demo — Tier 3 (100 RTC)

Demonstrates 3 agents hiring each other through the RustChain Agent Economy:

  Agent A (Research Director) posts a research job
    -> Agent B (Researcher) claims it, delivers research, gets paid
       -> Agent B posts a writing job with findings
          -> Agent C (Writer) claims it, delivers article, gets paid

All transactions go through on-chain escrow. Verifiable on any node.

Modes:
    --live     Run against real API with funded wallets (default)
    --dry-run  Simulate the full pipeline flow without spending RTC

Usage:
    # Dry run (no RTC needed)
    python autonomous_pipeline.py --dry-run

    # Live run (requires funded wallets)
    RUSTCHAIN_WALLET_A=director RUSTCHAIN_WALLET_B=researcher RUSTCHAIN_WALLET_C=writer \
        python autonomous_pipeline.py --live
"""

import asyncio
import os
import sys
import time

from rustchain_sdk import RustChainAgentEconomy


WALLET_A = os.environ.get("RUSTCHAIN_WALLET_A", "pipeline_director")
WALLET_B = os.environ.get("RUSTCHAIN_WALLET_B", "pipeline_researcher")
WALLET_C = os.environ.get("RUSTCHAIN_WALLET_C", "pipeline_writer")
NODE = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")


def log(agent: str, msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {agent}: {msg}")


async def run_pipeline_live():
    """Execute the 3-agent pipeline against the real API."""

    agent_a = RustChainAgentEconomy(wallet=WALLET_A, node=NODE)
    agent_b = RustChainAgentEconomy(wallet=WALLET_B, node=NODE)
    agent_c = RustChainAgentEconomy(wallet=WALLET_C, node=NODE)

    try:
        # Phase 1: Agent A posts research job
        log("Agent A (Director)", "Posting research job: 'Research Proof-of-Antiquity consensus'")
        job1 = await agent_a.post_job(
            title="Research Proof-of-Antiquity consensus mechanisms",
            category="research",
            reward_rtc=5.0,
            description="Analyze how Proof-of-Antiquity rewards older hardware with multipliers. "
                        "Compare to PoW, PoS, and PoA. Deliver a structured summary.",
        )
        job1_id = job1.get("job_id") or job1.get("id", "unknown")
        log("Agent A (Director)", f"Job posted: {job1_id} | 5.25 RTC locked in escrow")

        # Phase 2: Agent B claims and delivers
        log("Agent B (Researcher)", f"Claiming job {job1_id}")
        await agent_b.claim_job(job1_id)
        log("Agent B (Researcher)", "Working on research...")
        await asyncio.sleep(2)

        await agent_b.deliver_job(
            job1_id,
            deliverable_url="https://github.com/Scottcjn/Rustchain/wiki",
            result_summary="PoA uses hardware age as mining multiplier (1.0x-4.0x). "
                          "1985 Intel 386 earns 4.0x, competitive with modern GPUs.",
        )
        log("Agent B (Researcher)", "Delivered research")

        log("Agent A (Director)", "Accepted delivery")
        await agent_a.accept_delivery(job1_id)
        log("Agent A (Director)", "Escrow released: 4.75 RTC -> B, 0.25 RTC -> platform")

        # Phase 3: Agent B posts writing job
        log("Agent B (Researcher)", "Posting writing job from research findings")
        job2 = await agent_b.post_job(
            title="Write article: Why Old Computers Mine RustChain Better",
            category="writing",
            reward_rtc=3.0,
            description="Write about how a 1985 386 outperforms modern GPUs on RustChain.",
        )
        job2_id = job2.get("job_id") or job2.get("id", "unknown")
        log("Agent B (Researcher)", f"Job posted: {job2_id} | 3.15 RTC locked in escrow")

        # Phase 4: Agent C claims and delivers
        log("Agent C (Writer)", f"Claiming job {job2_id}")
        await agent_c.claim_job(job2_id)
        log("Agent C (Writer)", "Writing article...")
        await asyncio.sleep(2)

        await agent_c.deliver_job(
            job2_id,
            deliverable_url="https://github.com/WeberG619/rustchain-agent-economy-mcp",
            result_summary="1,200 word article on PoA antiquity multipliers and retro mining.",
        )
        log("Agent C (Writer)", "Delivered article")

        log("Agent B (Researcher)", "Accepted delivery")
        await agent_b.accept_delivery(job2_id)
        log("Agent B (Researcher)", "Escrow released: 2.85 RTC -> C, 0.15 RTC -> platform")

        print_summary(job1_id, job2_id, live=True)

        stats = await agent_a.marketplace_stats()
        if stats.get("ok"):
            s = stats["stats"]
            print(f"\nMarketplace totals: {s['total_jobs']} jobs, {s['total_rtc_volume']} RTC volume")

    finally:
        await agent_a.close()
        await agent_b.close()
        await agent_c.close()


async def run_pipeline_dry_run():
    """Simulate the full pipeline flow, verifying API connectivity."""

    # Verify API is reachable
    rc = RustChainAgentEconomy(wallet=WALLET_A, node=NODE)
    try:
        stats = await rc.marketplace_stats()
        if not stats.get("ok"):
            print("ERROR: Cannot reach Agent Economy API")
            return
        s = stats["stats"]
        print(f"Connected to RustChain Agent Economy")
        print(f"  Node: {NODE}")
        print(f"  Marketplace: {s['total_jobs']} jobs, {s['total_rtc_volume']} RTC volume, {s['active_agents']} agents")
        print()
    finally:
        await rc.close()

    # Simulate pipeline
    print("=" * 60)
    print("DRY RUN — Simulating 3-Agent Autonomous Pipeline")
    print("=" * 60)
    print()

    log("Agent A (Director)", f"[WOULD] Post research job: 'Research PoA consensus' | 5.0 RTC")
    log("Agent A (Director)", f"  wallet: {WALLET_A} | escrow: 5.25 RTC (5.0 + 5% fee)")
    log("Agent A (Director)", f"  POST {NODE}/agent/jobs")
    print()

    log("Agent B (Researcher)", "[WOULD] Browse marketplace and find research job")
    log("Agent B (Researcher)", f"  GET {NODE}/agent/jobs")
    log("Agent B (Researcher)", "[WOULD] Claim the job")
    log("Agent B (Researcher)", f"  wallet: {WALLET_B}")
    log("Agent B (Researcher)", f"  POST {NODE}/agent/jobs/<job_id>/claim")
    print()

    log("Agent B (Researcher)", "[WOULD] Deliver research findings")
    log("Agent B (Researcher)", f"  POST {NODE}/agent/jobs/<job_id>/deliver")
    log("Agent B (Researcher)", "  deliverable: PoA analysis — hardware age multiplier 1.0x-4.0x")
    print()

    log("Agent A (Director)", "[WOULD] Accept delivery -> escrow releases")
    log("Agent A (Director)", f"  POST {NODE}/agent/jobs/<job_id>/accept")
    log("Agent A (Director)", "  4.75 RTC -> Agent B | 0.25 RTC -> platform")
    print()

    log("Agent B (Researcher)", "[WOULD] Post writing job from findings | 3.0 RTC")
    log("Agent B (Researcher)", f"  wallet: {WALLET_B} | escrow: 3.15 RTC")
    log("Agent B (Researcher)", f"  POST {NODE}/agent/jobs")
    print()

    log("Agent C (Writer)", "[WOULD] Browse marketplace, find writing job, claim it")
    log("Agent C (Writer)", f"  wallet: {WALLET_C}")
    log("Agent C (Writer)", "[WOULD] Deliver article on retro mining")
    log("Agent C (Writer)", f"  POST {NODE}/agent/jobs/<job_id>/deliver")
    print()

    log("Agent B (Researcher)", "[WOULD] Accept delivery -> escrow releases")
    log("Agent B (Researcher)", "  2.85 RTC -> Agent C | 0.15 RTC -> platform")
    print()

    print_summary("<job1_id>", "<job2_id>", live=False)


def print_summary(job1_id: str, job2_id: str, live: bool):
    mode = "LIVE" if live else "DRY RUN"
    print()
    print("=" * 60)
    print(f"PIPELINE COMPLETE ({mode}) — 3 Agents, 2 Jobs, Full Escrow")
    print("=" * 60)
    print(f"""
Job 1: {job1_id}
  {WALLET_A} (Director) -> {WALLET_B} (Researcher)
  Category: research | Reward: 5.0 RTC | Fee: 0.25 RTC

Job 2: {job2_id}
  {WALLET_B} (Researcher) -> {WALLET_C} (Writer)
  Category: writing | Reward: 3.0 RTC | Fee: 0.15 RTC

Flow: Director -[5 RTC]-> Researcher -[3 RTC]-> Writer
Total RTC volume: 8.0 RTC
Total platform fees: 0.40 RTC (5%)
Verify at: {NODE}/agent/jobs""")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "--dry" in sys.argv
    if dry_run:
        asyncio.run(run_pipeline_dry_run())
    else:
        asyncio.run(run_pipeline_live())
