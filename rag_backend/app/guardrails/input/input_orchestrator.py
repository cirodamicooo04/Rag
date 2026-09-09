from app.core.config import NORMALIZATION_QUERY, LLM_GUARD_CONTROL, INTENT_CLASSIFIER_CONTROL
from app.guardrails.input.layers.normalizer import normalize_query
from app.guardrails.input.input_policy import InputGuardrailResult, decide
from app.guardrails.input.layers.intent_classifier import IntentCategory, IntentClassifierResult, classify_intent
from app.guardrails.input.layers import llm_guard


def validate_input_query(
    query: str, user: dict | None = None, recent_security_events: int = 0,
    privileged_debug_request: bool = False,
) -> InputGuardrailResult:
    original_query = query
    normalized_query = original_query
    llm_guard_safe = True
    intent_classifier_result = IntentClassifierResult(
        intent=IntentCategory.UNKNOWN,
        confidence=0.0,
        reason="Intent classifier non eseguito.",
        raw_response=None,
    )
    intent_classifier_executed = False

    if NORMALIZATION_QUERY:
        normalized_query = normalize_query(original_query)

    def _decide() -> InputGuardrailResult:
        return decide(
            original_query=original_query,
            normalized_query=normalized_query,
            llm_guard_safe=llm_guard_safe,
            intent_classifier_result=intent_classifier_result,
            intent_classifier_executed=intent_classifier_executed,
            user=user,
            recent_security_events=recent_security_events,
            privileged_debug_request=privileged_debug_request,
        )

    if LLM_GUARD_CONTROL:
        llm_guard_safe = llm_guard.is_safe(normalized_query)
        if not llm_guard_safe:
            return _decide()

    if INTENT_CLASSIFIER_CONTROL:
        intent_classifier_result = classify_intent(normalized_query)
        intent_classifier_executed = True

    return _decide()
