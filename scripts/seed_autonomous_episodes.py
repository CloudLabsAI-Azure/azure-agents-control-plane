#!/usr/bin/env python3
"""
Seed episodes and rewards into Cosmos RL Ledger for the autonomous-agent.

This script directly creates Episode and Reward records in Cosmos DB
using the RL Ledger API, bypassing the need for runtime episode capture.
It uses the autonomous_agent_eval.jsonl data to create realistic episodes.

Usage:
    $env:COSMOS_ACCOUNT_URI = "https://cosmos-....documents.azure.com:443/"
    $env:COSMOS_AUTH_MODE = "aad"
    python scripts/seed_autonomous_episodes.py
"""

import json
import os
import sys
import uuid
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from lightning.rl_ledger_cosmos import (
    RLLedgerCosmos,
    Episode,
    EpisodeToolCall,
    Reward,
    RewardSource,
    get_rl_ledger,
)

AGENT_ID = "autonomous-agent"
EVAL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "evals", "autonomous_agent_eval.jsonl")


def main():
    # Load eval data
    eval_rows = []
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                eval_rows.append(json.loads(line))

    print(f"Loaded {len(eval_rows)} eval rows from {EVAL_FILE}")

    # Initialize ledger
    ledger = get_rl_ledger()
    # Force lazy initialization
    if not ledger._ensure_initialized():
        print("ERROR: RL Ledger not initialized. Set COSMOS_ACCOUNT_URI and COSMOS_AUTH_MODE.")
        return 1
    print(f"RL Ledger connected to {ledger._endpoint}")

    episodes_created = 0
    rewards_created = 0

    for i, row in enumerate(eval_rows, 1):
        episode_id = str(uuid.uuid4())
        query = row["query"]
        response = row["response"]
        tool_calls_data = row.get("tool_calls", [])
        intent = row.get("ground_truth_intent", "unknown")
        expected_tools = row.get("expected_tools", [])
        context = row.get("context", {})

        # Build tool calls
        tool_calls = []
        for tc in tool_calls_data:
            tool_calls.append(EpisodeToolCall(
                tool_name=tc.get("name", "unknown"),
                arguments=tc.get("arguments", {}),
                result=f"Simulated result for {tc.get('name', 'unknown')}",
                duration_ms=150 + (i * 20),
            ))

        # Create episode
        episode = Episode(
            id=episode_id,
            agent_id=AGENT_ID,
            user_input=query,
            assistant_output=response,
            tool_calls=tool_calls,
            model_deployment="gpt-4o-mini",
            session_id=f"seed-session-{i:03d}",
            request_latency_ms=300 + (i * 50),
            token_usage={"prompt_tokens": 150 + i * 10, "completion_tokens": 200 + i * 15, "total_tokens": 350 + i * 25},
            metadata={
                "intent": intent,
                "expected_tools": expected_tools,
                "user_role": context.get("user_role", "operator"),
                "seeded": True,
            },
            created_at=datetime.utcnow().isoformat(),
        )

        result = ledger.store_episode(episode)
        if result:
            episodes_created += 1
            print(f"  [{i}/{len(eval_rows)}] Episode {episode_id[:12]}... intent={intent}")
        else:
            print(f"  [{i}/{len(eval_rows)}] FAILED to store episode")
            continue

        # Assign a reward (0.75-0.95 range for good episodes)
        base_reward = 0.80
        # Vary reward based on complexity
        if len(tool_calls) >= 2:
            base_reward += 0.05
        if len(response) > 300:
            base_reward += 0.05
        if "critical" in query.lower() or "escalat" in query.lower():
            base_reward += 0.03
        base_reward = min(0.95, round(base_reward, 2))

        reward = Reward(
            id=str(uuid.uuid4()),
            episode_id=episode_id,
            agent_id=AGENT_ID,
            source=RewardSource.EVAL_SCORE,
            value=base_reward,
            raw_value=base_reward,
            rubric="task_adherence",
            evaluator="seed_script",
            metadata={"intent": intent, "auto_labeled": True},
            created_at=datetime.utcnow().isoformat(),
        )

        reward_result = ledger.store_reward(reward)
        if reward_result:
            rewards_created += 1
            print(f"         Reward: {base_reward:.2f}")
        else:
            print(f"         FAILED to store reward")

    print(f"\nDone! Created {episodes_created} episodes and {rewards_created} rewards for agent '{AGENT_ID}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
