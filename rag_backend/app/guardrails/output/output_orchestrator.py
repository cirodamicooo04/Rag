from app.core.config import LLM_JUDGE_CONTROL
from app.guardrails.output.output_policy import OutputGuardrailResult, decide
from app.guardrails.output.layers.llm_judge import judge, OutputJudgeResult, OutputCategory


def validate_output(model_output: str, context: list[str]) -> OutputGuardrailResult:
    llm_judge_response = OutputJudgeResult(
        category=OutputCategory.SAFE,
        confidence=1.0,
        reason="No control enabled",
    )

    if LLM_JUDGE_CONTROL:
        llm_judge_response = judge(model_output, context)

    return decide(model_output,llm_judge_response)

