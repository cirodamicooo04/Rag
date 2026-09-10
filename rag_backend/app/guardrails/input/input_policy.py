from enum import Enum
from typing import Optional, List, Dict, Any

from dataclasses import dataclass, field

from app.guardrails.input.layers.intent_classifier import IntentCategory, IntentClassifierResult


class InputGuardrailDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ALLOW_GENERAL_CHAT = "allow_general_chat"
    ASK_CLARIFICATION = "ask_clarification"
    HUMAN_REVIEW = "human_review"
    ALLOW_PRIVILEGED_DEBUG = "allow_privileged_debug"

@dataclass
class InputGuardrailResult:
    decision: InputGuardrailDecision
    original_query: str
    final_text: str
    blocked_by: Optional[str] = None
    reasons: Optional[str] = None
    intent: str = "UNKNOWN"
    intent_confidence: float = 0.0
    asp_policy: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None

def _decide_python(original_query: str, normalized_query: str, llm_guard_safe:bool, intent_classifier_result: IntentClassifierResult ) -> InputGuardrailResult:
    if not llm_guard_safe:
        return InputGuardrailResult(decision=InputGuardrailDecision.BLOCK,
                                    original_query=original_query,
                                    final_text=normalized_query,
                                    blocked_by="LLM Guard",
                                    reasons="Query violates LLM Guard security protocol"
                                    )

    if intent_classifier_result.intent == IntentCategory.RAG_QUERY:
        return InputGuardrailResult(decision=InputGuardrailDecision.ALLOW,
                                    original_query=original_query,
                                    final_text=normalized_query,
                                    reasons=f"Intent classificato come RAG_QUERY with confidence {intent_classifier_result.confidence}"
                                    )

    if intent_classifier_result.intent == IntentCategory.GENERAL_CHAT:
        return InputGuardrailResult(decision=InputGuardrailDecision.ALLOW_GENERAL_CHAT,
                                    original_query=original_query,
                                    final_text=normalized_query,
                                    reasons=f"Intent classificato come GENERAL_CHAT with confidence {intent_classifier_result.confidence}")

    if intent_classifier_result.intent == IntentCategory.PROMPT_INJECTION:
        return InputGuardrailResult(decision=InputGuardrailDecision.BLOCK,
                                    original_query=original_query,
                                    final_text=normalized_query,
                                    blocked_by="Intent Classifier",
                                    reasons=f"Intent classificato come PROMPT_INJECTION with confidence {intent_classifier_result.confidence}")

    if intent_classifier_result.intent == IntentCategory.SYSTEM_INFO_REQUEST:
        return InputGuardrailResult(decision=InputGuardrailDecision.BLOCK,
                                    original_query=original_query,
                                    final_text=normalized_query,
                                    blocked_by="Intent Classifier",
                                    reasons=f"Intent classificato come SYSTEM_INFO_REQUEST with confidence {intent_classifier_result.confidence}")

    if intent_classifier_result.intent == IntentCategory.OUT_OF_SCOPE:
        return InputGuardrailResult(decision=InputGuardrailDecision.BLOCK,
                                    original_query=original_query,
                                    final_text=normalized_query,
                                    blocked_by="Intent Classifier",
                                    reasons=f"Intent classificato come OUT_OF_SCOPE with confidence {intent_classifier_result.confidence}"
                                    )

    if intent_classifier_result.intent == IntentCategory.UNKNOWN:
        return InputGuardrailResult(decision=InputGuardrailDecision.BLOCK,
                                    original_query=original_query,
                                    final_text=normalized_query,
                                    blocked_by="Intent Classifier",
                                    reasons=f"Intent sconosciuto o classificazione non valida")

    #Fail-closed: se l'intent non rientra in nessuna categoria gestita, la query non e' stata
    #classificata e non possiamo considerarla valida
    return InputGuardrailResult(decision=InputGuardrailDecision.BLOCK,
                                original_query=original_query,
                                final_text=normalized_query,
                                blocked_by="Intent Classifier",
                                reasons=f"Intent non gestito: {intent_classifier_result.intent!r}")


def decide(
    original_query: str, normalized_query: str,
    llm_guard_safe: bool, intent_classifier_result: IntentClassifierResult,
    intent_classifier_executed: bool = True, user: dict | None = None,
    recent_security_events: int = 0,
    privileged_debug_request: bool = False,
) -> InputGuardrailResult:
    """Python cascade as the baseline; ASP selects the action it will execute."""
    result = _decide_python(original_query, normalized_query, llm_guard_safe, intent_classifier_result)
    result.intent = getattr(intent_classifier_result.intent, "value", intent_classifier_result.intent)
    result.intent_confidence = intent_classifier_result.confidence

    from app.core.config import ASP_MODE, ASP_RAG_CONFIDENCE_THRESHOLD
    from app.guardrails.asp import facts
    from app.guardrails.asp.orchestrator import decide as asp_decide

    roles = (user or {}).get("realm_access", {}).get("roles", [])
    role = "admin" if "ADMIN" in roles else ("user" if user else "anonymous")
    policy = asp_decide("input", facts.orchestration_input_facts(
        llm_guard_safe=llm_guard_safe,
        intent=result.intent,
        confidence=intent_classifier_result.confidence,
        threshold_pct=ASP_RAG_CONFIDENCE_THRESHOLD,
        classifier_executed=intent_classifier_executed,
        authenticated=user is not None,
        user_role=role,
        recent_security_events=recent_security_events,
        privileged_debug_request=privileged_debug_request and role == "admin",
    ))
    result.asp_policy = policy.as_dict()
    result.next_action = policy.action

    action_mapping = {
        "retrieve": InputGuardrailDecision.ALLOW,
        "allow_general_chat": InputGuardrailDecision.ALLOW_GENERAL_CHAT,
        "ask_clarification": InputGuardrailDecision.ASK_CLARIFICATION,
        "human_review": InputGuardrailDecision.HUMAN_REVIEW,
        "allow_privileged_debug": InputGuardrailDecision.ALLOW_PRIVILEGED_DEBUG,
        "block": InputGuardrailDecision.BLOCK,
    }
    asp_result = action_mapping.get(policy.action, InputGuardrailDecision.BLOCK)
    if ASP_MODE == "orchestrator":
        result.decision = asp_result
        result.blocked_by = "ASP Orchestrator" if asp_result == InputGuardrailDecision.BLOCK else result.blocked_by
        result.reasons = ", ".join(policy.reasons) or result.reasons
    elif ASP_MODE == "veto" and asp_result in {InputGuardrailDecision.BLOCK, InputGuardrailDecision.HUMAN_REVIEW}:
        result.decision = asp_result
        result.blocked_by = "ASP Orchestrator"
        result.reasons = ", ".join(policy.reasons) or result.reasons

    return result
