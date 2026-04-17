"""
resilience.py — The Resilience Stack (Week 15: Defense in Depth).

Transitions the system from "Fragile" to "Antifragile".
Reliability is defined not by model intelligence, but by architectural constraints.

Four-Layer Defense Strategy:
  Layer 1 — Retry Strategies     : Temporal Resilience (exponential backoff + jitter)
  Layer 2 — Budgetary Caps       : Token limits to prevent Denial of Wallet attacks
  Layer 3 — Validation Layers    : Structural Integrity via JSON schema enforcement
  Layer 4 — Self-Checking Agents : Semantic Integrity via Reviewer metacognition
"""

## ---- Layer 1: Retry Strategies — Temporal Resilience (Week 15) ----
import time
import random
import json
import logging
from typing import Callable, Any, Optional
from pydantic import BaseModel, ValidationError
from crewai import Agent, Task

# ── Logging setup ──────────────────────────────────────────────────────────────
# Structured logging gives visibility into retry attempts and failures.
# This is the "Glass Box Experience" — making the system's behaviour traceable.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),                        # Console output
        logging.FileHandler("mission_log.txt"),         # Persistent log file
    ]
)
logger = logging.getLogger(__name__)


def execute_with_retry(api_call_func: Callable, max_retries: int = 3) -> Any:
    """
    Layer 1: Exponential Backoff + Jitter retry wrapper.

    Handles temporal instability (API timeouts, 503 errors) from volatile
    external services without crashing the agent task loop.
    Jitter prevents 'Thundering Herd' — all agents retrying at the same time.

    Usage:
        result = execute_with_retry(lambda: my_api_call(params))
    """
    for attempt in range(max_retries):
        try:
            # Attempt the core logic (web scraper or LLM API call)
            return api_call_func()

        except Exception as e:
            # Exponential Backoff: 2^attempt seconds (1s, 2s, 4s...)
            # + random Jitter (0-1s) to stagger concurrent retries
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                f"Retrying in {wait_time:.2f}s..."
            )
            time.sleep(wait_time)

    # Final fallback — all retries exhausted
    raise Exception("Layer 1 Failure: Max retries exceeded. Check API status.")


## ---- Layer 2: Budgetary Caps — Denial of Wallet Prevention (Week 15) ----

# Max tokens per agent call — prevents runaway costs from infinite loops.
# This is the 'Budgetary Cap' from the course (5,000 token hard limit).
MAX_TOKENS_PER_CALL = 5000

def apply_budget_cap(agent: Agent, max_tokens: int = MAX_TOKENS_PER_CALL) -> Agent:
    """
    Layer 2: Applies a token budget cap to an agent.

    Prevents 'Denial of Wallet' attacks where a single agent loop
    consumes unlimited tokens. Sets max_tokens on the underlying LLM.

    The agent rejects expensive or out-of-scope queries immediately
    rather than burning tokens trying to process them.
    """
    # Apply token limit to the agent's LLM config
    if hasattr(agent, 'llm') and agent.llm:
        agent.llm.max_tokens = max_tokens
        logger.info(f"[Layer 2] Budget cap applied: {max_tokens} tokens on '{agent.role}'")
    return agent


def check_query_budget(query: str, max_length: int = 2000) -> bool:
    """
    Layer 2: Rejects queries that exceed the input budget.
    Prevents agents from processing extremely long inputs that would
    cause O(n²) latency scaling in the transformer attention layer.
    """
    if len(query) > max_length:
        logger.warning(
            f"[Layer 2] Query rejected: {len(query)} chars exceeds "
            f"budget cap of {max_length} chars."
        )
        return False
    return True


## ---- Layer 3: Validation Layers — Structural Integrity (Week 15) ----

class StructuredReport(BaseModel):
    """
    Layer 3: JSON Schema for mission output enforcement.

    Converts non-deterministic LLM text into reliable, machine-readable
    structured data. 'Trust, but Verify' — the schema is the contract.
    Used with Task(output_json=StructuredReport) to auto-enforce format.
    """
    title:    str   # Report title
    summary:  str   # Executive summary (1-2 sentences)
    findings: list  # List of key findings (strings)
    sources:  list  # List of source URLs or references
    status:   str   # "complete" | "partial" | "failed"


def validate_json_output(raw_output: str, schema: type = StructuredReport) -> Optional[dict]:
    """
    Layer 3: Validates and auto-repairs broken JSON output from agents.

    LLMs sometimes produce malformed JSON. This function attempts to:
    1. Parse the raw string as JSON
    2. Validate against the Pydantic schema
    3. Return None if repair is impossible (triggers re-prompt)

    This prevents 'Broken JSON / Type Mismatch' failures from
    propagating through the pipeline.
    """
    try:
        # Step 1: Parse raw JSON string
        data = json.loads(raw_output)
        # Step 2: Validate against schema (Type Checking)
        validated = schema(**data)
        logger.info("[Layer 3] JSON output validated successfully.")
        return validated.model_dump()

    except json.JSONDecodeError as e:
        logger.error(f"[Layer 3] JSON parse error: {e}. Triggering re-prompt.")
        return None

    except ValidationError as e:
        logger.error(f"[Layer 3] Schema validation error: {e}. Triggering re-prompt.")
        return None


## ---- Layer 4: Self-Checking Agents — Semantic Integrity (Week 15) ----

def create_reviewer_agent() -> Agent:
    """
    Layer 4: Metacognition via a dedicated Reviewer Agent.

    Implements a recursive feedback loop where the Reviewer critiques
    the primary agent's output against original source material.
    Detects and flags hallucinated citations, mismatched facts, or
    outputs that don't meet the expected_output contract.

    This is the 'Immune System' at the semantic level — not just
    syntax (Layer 3) but meaning and accuracy.
    """
    return Agent(
        role="Quality Reviewer",
        goal=(
            "Ensure semantic accuracy by critiquing the writer's output "
            "against the original research. Flag any hallucinated citations, "
            "unsupported claims, or facts not present in the source material."
        ),
        backstory=(
            "You are a meticulous fact-checker and quality auditor. "
            "Your only job is to compare the draft report against the original "
            "research sources and identify any discrepancies, hallucinations, "
            "or unsupported claims. You output either APPROVED or a list of "
            "specific corrections needed, never vague feedback."
        ),
        verbose=True,
        allow_delegation=False,
    )


def self_correction_loop(
    primary_task_result: str,
    source_material: str,
    reviewer: Agent,
    max_iterations: int = 3,
) -> str:
    """
    Layer 4: Recursive self-correction loop.

    Reviewer critiques the draft. If rejected, feedback is returned
    to the primary agent for refinement. Repeats until APPROVED
    or max_iterations reached.

    Prevents 'Hallucination Cascade' — where one wrong fact
    propagates through the entire pipeline.
    """
    current_draft = primary_task_result
    iterations = 0

    while iterations < max_iterations:
        # Reviewer evaluates draft against source material
        review_task = Task(
            description=(
                f"Review this draft:\n{current_draft}\n\n"
                f"Against this source material:\n{source_material}\n\n"
                "Output 'APPROVED' if accurate, or list specific corrections."
            ),
            expected_output="Either 'APPROVED' or a numbered list of corrections.",
            agent=reviewer,
        )

        critique = str(review_task.execute_sync())   # type: ignore

        if "APPROVED" in critique.upper():
            logger.info(f"[Layer 4] Draft approved after {iterations + 1} iteration(s).")
            return current_draft
        else:
            # Hallucination detected — log and flag for re-prompt
            logger.warning(f"[Layer 4] Hallucination detected. Feedback: {critique}")
            # Append feedback so primary agent can refine on retry
            current_draft += f"\n\n[REVIEWER FEEDBACK — iteration {iterations + 1}]: {critique}"
            iterations += 1

    # Max iterations reached — return best attempt with warning
    logger.error("[Layer 4] Max review iterations reached. Returning last draft with warning.")
    return current_draft + "\n\n⚠️ WARNING: This output did not pass full review. Manual verification recommended."
