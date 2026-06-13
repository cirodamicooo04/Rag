
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.crud import crud_docs
from app.db.database import get_db
from app.schemas.ask_request import AskRequest
from app.schemas.conversation import SaveConversationRequest, ConversationResponse, ConversationMessageResponse
from app.security.auth_guard import get_optional_current_user, require_role
from app.services.query import get_answer

user_router = APIRouter( tags=["user"])

last_conversation = {}

@user_router.post("/ask")
async def ask_query(request: AskRequest, db: Session = Depends(get_db), user: dict | None = Depends(get_optional_current_user)):
    question = request.question

    if not question.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        answer = get_answer(user_query=question, user=user , db=db)

        global last_conversation
        last_conversation = {"question": question, "answer": answer}

        return {"answer": answer}
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")

@user_router.post("/conversations")
async def save_conversation(conv_to_save: SaveConversationRequest, user: dict = Depends(require_role("USER")), db: Session = Depends(get_db)):
    messages = conv_to_save.messages
    title = conv_to_save.conversation_title
    if not messages or len(messages) == 0:
        raise HTTPException(status_code=400, detail="Conversation is empty")

    if title is None or not title.strip():
        raise HTTPException(status_code=400, detail="Conversation title cannot be empty")

    if len(title) > 50:
        raise HTTPException(status_code=400, detail="Conversation title cannot exceed 50 characters")

    if len(messages) > 50:
        messages = messages[-50:]

    for message in messages:
        if message.role not in ["user", "assistant"]:
            raise HTTPException(status_code=400, detail="Conversation must contain only user and assistant messages")
        if message.content is None or not message.content.strip():
            raise HTTPException(status_code=400, detail="Conversation message content cannot be empty")
        if message.sequence_number is None or message.sequence_number < 0:
            raise HTTPException(status_code=400, detail="Conversation message sequence number must be a positive integer")
        if len(message.content) > 10000:
            raise HTTPException(status_code=400, detail="Conversation message content cannot exceed 10000 characters")


    conv = crud_docs.create_conversation(db, user.get("sub"), title)
    crud_docs.save_conversation_messages(db, conv.id, messages)

    return {"message": "Conversation saved successfully"}



@user_router.get("/conversations")
async def get_saved_conversations(user: dict = Depends(require_role("USER")),db: Session = Depends(get_db)):
    conversations = crud_docs.get_saved_conversations(db, user.get("sub"))

    response = []
    for conv in conversations:
        response.append( ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            messages=[
                ConversationMessageResponse(
                    id=message.id,
                    role=message.role,
                    sequence_number=message.sequence_number,
                    content=message.content
                ) for message in conv.messages
            ]
        ))
    return response


@user_router.delete("/conversations/{id}", dependencies=[Depends(require_role("USER"))])
def delete_conversation(id: int, user: dict = Depends(require_role("USER")), db: Session = Depends(get_db)):
    conversation = crud_docs.get_saved_conversation_by_id(db, id)

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user.get("sub"):
        raise HTTPException(status_code=403, detail="You do not have permission to delete this conversation")

    crud_docs.delete_conversation_by_id(db, id)

    return {"message": "Conversation deleted successfully"}
