from fastapi import Depends, HTTPException, Request
from ..services.retriever_service import qa_chain
from ..services.crud_service import update_conversation
import uuid
from sqlalchemy.orm import Session
from ..database.postgres import get_db
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()

class AskQuestion(BaseModel): # pydantic model 
    session_id: uuid.UUID
    session_name: str
    question: str
    
@router.post("/qa/")
async def question_answer(
    ask_question: AskQuestion, 
    request: Request, 
    db: Session = Depends(get_db)
):
    try:
        store = request.app.state.retriever_store
        history = request.app.state.chat_history

        # Lấy retriever và chat history từ store
        if ask_question.session_id not in (store or history):
            raise HTTPException(status_code=404, detail="Retriever not found")
        
        retriever = store[ask_question.session_id]['retriever']
        chat_history = history[ask_question.session_id]['chat history']
        
        # Gọi hàm xử lý câu hỏi
        answer = qa_chain(ask_question.question, retriever, chat_history)

        # Cập nhật hội thoại vào cơ sở dữ liệu
        update_conversation(db, ask_question.session_id, ask_question.question, answer)

        # Trả về kết quả
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
