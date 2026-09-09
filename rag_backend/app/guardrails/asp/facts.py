"""Translate Python guardrail signals into ASP facts.

The LLMs stay the *labelers*; here we only serialise their labels (plus the
deterministic safety booleans / retrieval counts) into the discrete fact
vocabulary the .lp policies reason over.
"""
import re
from typing import Any, List


_SAFE_ATOM = re.compile(r"^[a-z][a-z0-9_]*$")


def _conf_to_int(confidence: float) -> int:
    """Rescale a 0..1 confidence to a 0..100 integer (ASP has no floats)."""
    try:
        value = int(round(float(confidence) * 100))
    except (TypeError, ValueError):
        value = 0
    return max(0, min(100, value))


def _atom(value: str) -> str:
    """Normalise an enum value / label to a safe lowercase ASP constant."""
    atom = str(value).strip().lower()
    return atom if _SAFE_ATOM.fullmatch(atom) else "unknown"


def input_facts(
    *,
    llm_guard_safe: bool,
    intent: str,
    confidence: float,
    threshold_pct: int,
    intent_classifier_executed: bool = True,
) -> List[str]:
    return [
        f"signal_llm_guard({'safe' if llm_guard_safe else 'unsafe'}).",
        f"signal_intent_classifier({'executed' if intent_classifier_executed else 'skipped'}).",
        f"intent({_atom(intent)}).",
        f"confidence({_conf_to_int(confidence)}).",
        f"threshold({int(threshold_pct)}).",
    ]


def orchestration_input_facts(
    *, llm_guard_safe: bool, intent: str,
    confidence: float, threshold_pct: int, classifier_executed: bool,
    authenticated: bool = False, user_role: str = "anonymous",
    recent_security_events: int = 0,
    privileged_debug_request: bool = False,
) -> List[str]:
    facts = input_facts(
        llm_guard_safe=llm_guard_safe,
        intent=intent,
        confidence=confidence,
        threshold_pct=threshold_pct,
        intent_classifier_executed=classifier_executed,
    )
    facts.extend([
        f"authenticated({'true' if authenticated else 'false'}).",
        f"user_role({_atom(user_role)}).",
        f"recent_security_events({max(0, int(recent_security_events))}).",
    ])
    if privileged_debug_request:
        facts.append("privileged_debug_request.")
    return facts


def _pct(value: Any) -> int:
    """Accept either a 0..1 score or an already-percent score."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0
    if number <= 1.0:
        number *= 100
    return max(0, min(100, int(round(number))))


def retrieval_facts(
    *, chunks: List[dict], attempt: int, max_attempts: int,
    min_score: int, min_trust: int, min_chunks: int,
    context_consistency: str = "not_assessed",
) -> List[str]:
    consistency = _atom(context_consistency)
    if consistency not in {"consistent", "contradictory", "not_assessed", "unknown"}:
        consistency = "unknown"
    result = [
        f"retrieval_attempt({max(1, int(attempt))}).",
        f"max_retrieval_attempts({max(1, int(max_attempts))}).",
        f"min_retrieval_score({_pct(min_score)}).",
        f"min_document_trust({_pct(min_trust)}).",
        f"min_usable_chunks({max(1, int(min_chunks))}).",
        f"context_consistency({consistency}).",
    ]
    for index, chunk in enumerate(chunks, start=1):
        identifier = f"chunk_{index}"
        source = _atom(chunk.get("source") or f"unknown_source_{index}")
        result.extend([
            f"retrieved({identifier}).",
            f"retrieval_score({identifier},{_pct(chunk.get('score'))}).",
            f"document_trust({identifier},{_pct(chunk.get('trust'))}).",
            f"chunk_security({identifier},{_atom(chunk.get('security', 'safe'))}).",
            f"chunk_source({identifier},{source}).",
        ])
    return result


def orchestration_output_facts(
    *, judge_category: str, confidence: float, threshold_pct: int,
    context_chunks: int, input_intent: str, input_confidence: float,
    generation_attempt: int, max_generation_attempts: int,
) -> List[str]:
    return [
        f"judge({_atom(judge_category)}).",
        f"confidence({_conf_to_int(confidence)}).",
        f"threshold({int(threshold_pct)}).",
        f"context_chunks({max(0, int(context_chunks))}).",
        f"input_intent({_atom(input_intent)}).",
        f"input_confidence({_conf_to_int(input_confidence)}).",
        f"generation_attempt({max(1, int(generation_attempt))}).",
        f"max_generation_attempts({max(1, int(max_generation_attempts))}).",
    ]
