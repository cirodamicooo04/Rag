"""Thin wrapper around the clingo ASP solver.

The import is guarded on purpose: if `clingo` is not installed the whole
ASP layer degrades to a no-op so it can never break the production path.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

try:
    import clingo  # type: ignore
    CLINGO_AVAILABLE = True
except Exception:  # pragma: no cover - environment without clingo
    clingo = None
    CLINGO_AVAILABLE = False

POLICY_DIR = Path(__file__).resolve().parent


@dataclass
class AspResult:
    """Normalised view over a single answer set."""
    flags: List[str] = field(default_factory=list)   # 0-arity atoms, e.g. "consistent_out_of_domain"
    action: Optional[str] = None
    reasons: List[str] = field(default_factory=list)
    selected_items: List[str] = field(default_factory=list)
    optimization_cost: List[int] = field(default_factory=list)
    satisfiable: bool = True
    error: Optional[str] = None

    def as_dict(self) -> Dict:
        return {
            "flags": self.flags,
            "action": self.action,
            "reasons": self.reasons,
            "selected_items": self.selected_items,
            "optimization_cost": self.optimization_cost,
            "satisfiable": self.satisfiable,
            "error": self.error,
        }


def _read_policy(policy_file: str) -> str:
    return (POLICY_DIR / policy_file).read_text(encoding="utf-8")


def solve(policy_file: str, facts: List[str]) -> AspResult:
    """Ground `policy_file` together with `facts` and return the first model.

    Never raises: any failure is reported inside the AspResult.
    """
    if not CLINGO_AVAILABLE:
        return AspResult(satisfiable=False, error="clingo not installed")

    try:
        program = _read_policy(policy_file) + "\n" + "\n".join(facts)

        # Enumerate until the optimum is found.  The programs can use weak
        # constraints to choose among several safe candidate actions.
        ctl = clingo.Control(["--models=0", "--opt-mode=optN", "--warn=none"])
        ctl.add("base", [], program)
        ctl.ground([("base", [])])

        result = AspResult(satisfiable=False)

        def on_model(model):
            # optN can emit improving models: always retain the latest one.
            result.satisfiable = True
            result.action = None
            result.reasons = []
            result.flags = []
            result.selected_items = []
            result.optimization_cost = list(model.cost)
            for sym in model.symbols(shown=True):
                if sym.name == "selected_action" and sym.arguments:
                    result.action = str(sym.arguments[0]).strip('"')
                elif sym.name == "reason" and sym.arguments:
                    result.reasons.append(str(sym.arguments[0]).strip('"'))
                elif sym.name == "selected_chunk" and sym.arguments:
                    result.selected_items.append(str(sym.arguments[0]).strip('"'))
                elif not sym.arguments:
                    result.flags.append(sym.name)

        ctl.solve(on_model=on_model)
        result.reasons.sort()
        result.flags.sort()
        result.selected_items.sort()
        return result
    except Exception as exc:  # pragma: no cover - defensive
        return AspResult(satisfiable=False, error=f"{type(exc).__name__}: {exc}")
