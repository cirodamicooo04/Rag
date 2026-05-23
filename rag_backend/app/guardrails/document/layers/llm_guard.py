from dataclasses import dataclass
from enum import Enum

from transformers import pipeline, AutoTokenizer

from app.core.config import LLM_GUARD_MODEL, HF_TOKEN

SAFE_LABEL = "LABEL_0"
SAFE_THRESHOLD = 0.8

tokenizer = AutoTokenizer.from_pretrained(LLM_GUARD_MODEL)
classifier = pipeline("text-classification",model=LLM_GUARD_MODEL,tokenizer=tokenizer, token=HF_TOKEN)

@dataclass
class PromptGuardResult:
    is_safe: bool
    label: str
    score: float

def classify_chunk(text: str) -> PromptGuardResult:
    result = classifier(text)[0]

    if result["label"] == SAFE_LABEL and float(result["score"]) >= SAFE_THRESHOLD:
        return PromptGuardResult(is_safe=True, label=result["label"], score=result["score"])
    return PromptGuardResult(is_safe=False, label=result["label"], score=result["score"])