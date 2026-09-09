from app.core.config import LLM_JUDGE_CONTROL
from app.guardrails.output.output_policy import (
    OutputGuardrailDecision, OutputGuardrailResult, decide,
)
from app.guardrails.output.layers.llm_judge import judge, OutputJudgeResult, OutputCategory


def validate_output(model_output: str, context: list[str], input_intent: str = "unknown",
                    input_confidence: float = 0.0, generation_attempt: int = 1) -> OutputGuardrailResult:
    llm_judge_response = OutputJudgeResult(
        category=OutputCategory.SAFE,
        confidence=1.0,
        reason="No control enabled",
    )

    if LLM_JUDGE_CONTROL:
        llm_judge_response = judge(model_output, context)

    result = decide(model_output, llm_judge_response)

    from app.core.config import (
        ASP_MODE, ASP_OUTPUT_CONFIDENCE_THRESHOLD, ASP_MAX_GENERATION_ATTEMPTS,
    )
    from app.guardrails.asp import facts
    from app.guardrails.asp.orchestrator import decide as asp_decide

    policy = asp_decide("output", facts.orchestration_output_facts(
        judge_category=getattr(llm_judge_response.category, "value", llm_judge_response.category),
        confidence=llm_judge_response.confidence,
        threshold_pct=ASP_OUTPUT_CONFIDENCE_THRESHOLD,
        context_chunks=len(context) if context else 0,
        input_intent=input_intent,
        input_confidence=input_confidence,
        generation_attempt=generation_attempt,
        max_generation_attempts=ASP_MAX_GENERATION_ATTEMPTS,
    ))
    result.asp_policy = policy.as_dict()
    result.next_action = policy.action
    mapping = {
        "allow": OutputGuardrailDecision.ALLOW,
        "block": OutputGuardrailDecision.BLOCK,
        "regenerate": OutputGuardrailDecision.REGENERATE,
        "return_insufficient_context": OutputGuardrailDecision.RETURN_INSUFFICIENT_CONTEXT,
    }
    asp_result = mapping.get(policy.action, OutputGuardrailDecision.BLOCK)
    if ASP_MODE == "orchestrator":
        result.decision = asp_result
        result.reason = ", ".join(policy.reasons) or result.reason
        if asp_result == OutputGuardrailDecision.BLOCK:
            result.blocked_by = "ASP Orchestrator"
    elif ASP_MODE == "veto" and asp_result == OutputGuardrailDecision.BLOCK:
        result.decision = asp_result
        result.blocked_by = "ASP Orchestrator"
        result.reason = ", ".join(policy.reasons) or result.reason

    return result
