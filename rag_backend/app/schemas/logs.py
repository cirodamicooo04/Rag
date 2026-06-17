from app.schemas.utils import CamelModel


class LogResponse(CamelModel):
    id: int
    user_id: str
    original_query: str
    final_query: str
    blocked_stage: str
    blocked_by: str
    reason: str
    created_at: str