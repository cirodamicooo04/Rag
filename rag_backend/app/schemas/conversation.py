from pydantic import BaseModel

class ConversationSchema(BaseModel):
    role: str
    content: str
    sequence_number: int

class SaveConversationRequest(BaseModel):
    conversation_title: str
    messages: list[ConversationSchema]

class ConversationMessageResponse(BaseModel):
    id: int
    role: str
    sequence_number: int
    content: str

class ConversationResponse(BaseModel):
    id: int
    user_id: str
    title: str
    messages: list[ConversationMessageResponse]



