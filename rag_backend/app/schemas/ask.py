from typing import Optional, Dict, Any, List, Set

from pydantic import ConfigDict

from app.schemas.utils import CamelModel


class RetrievedNode(CamelModel):
    rank: int
    score: Optional[float] = None
    node_id: Optional[str] = None
    text: str
    metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class AskResponse(CamelModel):
    answer: str
    original_query: Optional[str] = None
    final_query: Optional[str] = None
    retrieved_context: Optional[List[RetrievedNode]] = None
    asp_debug: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)