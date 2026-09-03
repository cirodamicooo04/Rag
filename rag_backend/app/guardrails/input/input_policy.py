from enum import Enum
from typing import Optional, List

from dataclasses import dataclass, field

from app.guardrails.input.layers.intent_classifier import IntentCategory, IntentClassifierResult


class InputGuardrailDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ALLOW_GENERAL_CHAT = "allow_general_chat"

@dataclass
class InputGuardrailResult:
    decision: InputGuardrailDecision
    original_query: str
    final_text: str
    blocked_by: Optional[str] = None
    reasons: Optional[str] = None

def decide(original_query: str, normalized_query: str, llm_guard_safe:bool, intent_classifier_result: IntentClassifierResult ) -> InputGuardrailResult:
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