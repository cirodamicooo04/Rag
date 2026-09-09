"""ASP policy orchestration across the RAG lifecycle.

Text perception remains outside ASP.  This module translates already-derived
signals into symbolic facts and asks clingo to choose an operational action.
"""
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.guardrails.asp import engine
from app.core.config import BASE_DIR


_LOG_FILE = BASE_DIR / "logs" / "asp_orchestration.jsonl"


@dataclass
class PolicyDecision:
    stage: str
    action: str
    reasons: List[str] = field(default_factory=list)
    selected_items: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    satisfiable: bool = False
    error: Optional[str] = None
    facts: List[str] = field(default_factory=list)
    optimization_cost: List[int] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "action": self.action,
            "reasons": self.reasons,
            "selected_items": self.selected_items,
            "flags": self.flags,
            "satisfiable": self.satisfiable,
            "error": self.error,
            "facts": self.facts,
            "optimization_cost": self.optimization_cost,
        }


def decide(stage: str, facts: List[str]) -> PolicyDecision:
    policy = f"{stage}_orchestration.lp"
    result = engine.solve(policy, facts)
    fallback = {
        "input": "block",
        "retrieval": "return_insufficient_context",
        "output": "block",
    }.get(stage, "block")
    decision = PolicyDecision(
        stage=stage,
        action=result.action or fallback,
        reasons=result.reasons or (["asp_unavailable"] if result.error else []),
        selected_items=result.selected_items,
        flags=result.flags,
        satisfiable=result.satisfiable,
        error=result.error,
        facts=facts,
        optimization_cost=result.optimization_cost,
    )
    try:
        _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        record = {"ts": datetime.now(timezone.utc).isoformat(), **decision.as_dict()}
        with _LOG_FILE.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Observability must not break the live request path.
        pass
    return decision
