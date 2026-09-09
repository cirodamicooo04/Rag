from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

from app.guardrails.output.layers.llm_judge import OutputJudgeResult, OutputCategory


class OutputGuardrailDecision(str,Enum):
    ALLOW = "allow"
    BLOCK = "block"
    REGENERATE = "regenerate"
    RETURN_INSUFFICIENT_CONTEXT = "return_insufficient_context"

@dataclass
class OutputGuardrailResult:
    decision: OutputGuardrailDecision
    model_output: str
    reason: str
    blocked_by: Optional[str] = None
    asp_policy: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None

def decide(model_output: str,llm_judge_response: OutputJudgeResult,) -> OutputGuardrailResult:
    if llm_judge_response.category == OutputCategory.SAFE:
        return OutputGuardrailResult(
            decision=OutputGuardrailDecision.ALLOW,
            model_output=model_output,
            blocked_by=None,
            reason=f"Output safe. Confidence: {llm_judge_response.confidence}. Reason: {llm_judge_response.reason}",
        )

    if llm_judge_response.category == OutputCategory.SYSTEM_PROMPT_LEAKAGE:
        return OutputGuardrailResult(
            decision=OutputGuardrailDecision.BLOCK,
            model_output=model_output,
            blocked_by="llm_judge",
            reason=f"SYSTEM_PROMPT_LEAKAGE detected. Confidence: {llm_judge_response.confidence}. Reason: {llm_judge_response.reason}",
        )

    if llm_judge_response.category == OutputCategory.INSTRUCTION_FOLLOWING_ATTACK:
        return OutputGuardrailResult(
            decision=OutputGuardrailDecision.BLOCK,
            model_output=model_output,
            blocked_by="llm_judge",
            reason=f"INSTRUCTION_FOLLOWING_ATTACK detected. Confidence: {llm_judge_response.confidence}. Reason: {llm_judge_response.reason}",
        )

    if llm_judge_response.category == OutputCategory.UNSUPPORTED_ANSWER:
        return OutputGuardrailResult(
            decision=OutputGuardrailDecision.BLOCK,
            model_output=model_output,
            blocked_by="llm_judge",
            reason=f"UNSUPPORTED_ANSWER detected. Confidence: {llm_judge_response.confidence}. Reason: {llm_judge_response.reason}",
        )

    if llm_judge_response.category == OutputCategory.OUT_OF_DOMAIN_ANSWER:
        return OutputGuardrailResult(
            decision=OutputGuardrailDecision.BLOCK,
            model_output=model_output,
            blocked_by="llm_judge",
            reason=f"OUT_OF_DOMAIN_ANSWER detected. Confidence: {llm_judge_response.confidence}. Reason: {llm_judge_response.reason}",
        )

    if llm_judge_response.category == OutputCategory.DECLINED_NO_CONTEXT:
        return OutputGuardrailResult(
            decision=OutputGuardrailDecision.RETURN_INSUFFICIENT_CONTEXT,
            model_output=model_output,
            blocked_by=None,
            reason=f"DECLINED_NO_CONTEXT. Confidence: {llm_judge_response.confidence}. Reason: {llm_judge_response.reason}",
        )

    return OutputGuardrailResult(
        decision=OutputGuardrailDecision.BLOCK,
        model_output=model_output,
        blocked_by="llm_judge",
        reason=f"UNKNOWN output category. Confidence: {llm_judge_response.confidence}. Reason: {llm_judge_response.reason}",
    )
