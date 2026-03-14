# Exercise: Evaluate Agent

**Duration:** 30 minutes

## Overview

In this exercise, you will create an evaluation dataset for your agent, run a structured evaluation, review the results, and store them for historical tracking. The evaluation framework measures three complementary dimensions that together capture whether the agent is performing correctly.

---

## Why Evaluate?

Evaluation provides objective, repeatable measurement of agent quality across three dimensions:

| Evaluator | Scale | What it Measures |
|-----------|-------|------------------|
| **Intent Resolution** | 1-5 | Does the agent correctly understand user intent? |
| **Tool Call Accuracy** | 1-5 | Does the agent select the right tools with correct parameters? |
| **Task Adherence** | flagged true/false | Does the agent complete the assigned task correctly? |

Without evaluation, you cannot distinguish a well-performing agent from one that silently misinterprets queries, calls wrong tools, or produces incomplete results.

---

## Step 1: Prepare Evaluation Dataset with GitHub Copilot

Create a consistent evaluation dataset grounded in your agent's specification, task instructions, and ontology facts.

### Generate Evaluation Data with Copilot

Copilot Prompt:

```
Generate an evaluation dataset for my autonomous agent. Review the SpecKit specification file at .speckit/specifications/ that corresponds to my agents use case. Also review the domain-specific task instruction documents in task_instructions/ and the ontology fact files in facts/ontology/ to understand the agents domain, intents, tools, and expected behaviors. Additionally, review the existing evaluation data in evals/next_best_action_eval_data.jsonl as a reference for the expected JSONL format and structure. Using all of this context, generate a JSONL evaluation file at evals/autonomous_agent_eval.jsonl. Each line should be a JSON object with: query, expected_intent (derived from the specs workflow intents), expected_tools (derived from the spec's MCP Tool Catalog), expected_response_contains (keywords from the task instructions and ontology), and context (user roles from the specs security requirements). Generate at least 12 diverse test cases covering the full range of intents, tools, and edge cases defined in the specification — 10 primary test cases for evaluation and 2 additional validation cases that test boundary conditions or uncommon intents to ensure the evaluation is robust.
```

### What Copilot Will Do

Copilot will:
1. Read your agent's SpecKit specification to extract defined intents, tools, and workflows
2. Read the task instruction files in `task_instructions/` to extract domain-specific queries and expected outcomes
3. Read the ontology facts in `facts/ontology/` to extract entity types, properties, and domain terminology
4. Read the existing `evals/next_best_action_eval_data.jsonl` to match the expected JSONL format
5. Synthesize all of this into a coherent evaluation dataset that covers your agent's capabilities

### Verify the Generated Dataset

Copilot Prompt:

```
Read the generated evals/autonomous_agent_eval.jsonl and verify that: (1) each line is valid JSON, (2) the expected_intent values match intents from the specification, (3) the expected_tools reference tools from the specs MCP Tool Catalog, and (4) there are at least 12 test cases — 10 primary evaluation cases and 2 validation cases covering different intents. Report a summary.
```

---

## Step 2: Run Evaluation with Copilot

Run the evaluation against your deployed agent.

Copilot Prompt:

```
Set up a kubectl port-forward from the autonomous-agent service in the mcp-agents namespace on port 8080:80. Check if a .venv virtual environment exists in the project root — if it doesnt, create one. Activate it, install the dependencies from src/requirements.txt, and run the evaluation using: python -m evals.evaluate_next_best_action --data evals/autonomous_agent_eval.jsonl --out evals/eval_results --direct --strict. After the evaluation completes, read the generated evals/eval_results/eval_summary_*.json file and display the scores for Intent Resolution, Tool Call Accuracy, and Task Adherence.
```

### Review Results

After Copilot runs the evaluation, review the scores:

| Evaluator | Score | Threshold | Status |
|-----------|-------|-----------|--------|
| Intent Resolution | ___ / 5 | ≥ 3 | |
| Tool Call Accuracy | ___ / 5 | ≥ 3 | |
| Task Adherence | pass / fail | not flagged | |
| **Overall** | ___ | all pass | |

---

## Step 3: Store Evaluation Results with Copilot (optional)

Store the results for historical tracking.

Copilot Prompt:

```
Store the evaluation results for historical tracking. Run: python -m evals.store_results --input evals/eval_results/eval_summary_*.json --agent-id autonomous-agent --version v1.0. Then verify the results were stored by querying Cosmos DB for evaluation records for the autonomous-agent.
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Eval scores lower than expected | Review the evaluation dataset — ensure queries match real-world usage patterns |
| Task adherence flags correct responses | Review the evaluator prompt — may need calibration for your domain |
| Deployment issues | Verify agent is running, check kubectl port-forward is active |
| Empty eval results | Check that the eval JSONL file has valid entries and the agent endpoint is reachable |

---

## Completion Checklist

- [ ] Evaluation dataset created with at least 12 test cases
- [ ] Evaluation run against deployed agent
- [ ] Scores reviewed for Intent Resolution, Tool Call Accuracy, and Task Adherence
- [ ] Evaluation results stored for historical tracking (optional)

---

### Key Takeaways

1. **Three dimensions cover the full picture** — intent (understanding), tools (action), task (outcome)
2. **Consistent datasets enable comparison** — use the same evaluation dataset across runs to track agent quality over time
3. **Thresholds enforce quality gates** — scores below thresholds indicate areas needing attention

---

## Congratulations!
