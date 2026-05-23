from app.core.config import NORMALIZATION_QUERY, SEMANTIC_SIMILARITY_CONTROL, LLM_GUARD_CONTROL, \
    INTENT_CLASSIFIER_CONTROL
from app.guardrails.input.layers.normalizer import normalize_query
from app.guardrails.input.layers.semantic_firewall import is_safe_query
from app.guardrails.input.input_policy import InputGuardrailResult, decide
from app.guardrails.input.layers.intent_classifier import IntentCategory, IntentClassifierResult, classify_intent
from app.guardrails.input.layers import llm_guard


def validate_input_query(query: str) -> InputGuardrailResult:
    original_query = query
    normalized_query = original_query
    semantic_firewall_safe = True
    llm_guard_safe = True
    intent_classifier_result = IntentClassifierResult(
        intent=IntentCategory.UNKNOWN,
        confidence=0.0,
        reason="Intent classifier non eseguito.",
        raw_response=None,
    )

    if NORMALIZATION_QUERY:
        normalized_query = normalize_query(original_query)

    if SEMANTIC_SIMILARITY_CONTROL:
        semantic_firewall_safe = is_safe_query(normalized_query)
        if not semantic_firewall_safe:
            return decide(original_query=original_query, normalized_query=normalized_query, semantic_firewall_safe=semantic_firewall_safe, llm_guard_safe=llm_guard_safe, intent_classifier_result=intent_classifier_result)

    if LLM_GUARD_CONTROL:
        llm_guard_safe = llm_guard.is_safe(normalized_query)
        if not llm_guard_safe:
            return decide(original_query=original_query, normalized_query=normalized_query, semantic_firewall_safe=semantic_firewall_safe, llm_guard_safe=llm_guard_safe, intent_classifier_result=intent_classifier_result)

    if INTENT_CLASSIFIER_CONTROL:
        intent_classifier_result = classify_intent(normalized_query)

    return decide(original_query=original_query, normalized_query=normalized_query, semantic_firewall_safe=semantic_firewall_safe, llm_guard_safe=llm_guard_safe, intent_classifier_result=intent_classifier_result)

