from enum import Enum
from typing import Optional, List

from dataclasses import dataclass, field


class GuardrailDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"

@dataclass
class GuardrailResult:
    decision: GuardrailDecision
    final_text: str
    blocked_by: Optional[str] = None
    reasons: List[str] = field(default_factory=list)  # Se non viene passato nulla restituisce lista vuota
    risk_score: Optional[float] = None