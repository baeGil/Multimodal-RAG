from fastapi import Depends, HTTPException
from ..services.crud_service import create_session
from sqlalchemy.orm import Session
from ..database.postgres import get_db
from fastapi import APIRouter
from pydantic import BaseModel 
import uuid

router = APIRouter()

class SessionCreate(BaseModel):
    session_name: str
    session_id: uuid.UUID

# Create new session
@router.post("/session/create/")
async def question_answer(session: SessionCreate, db: Session = Depends(get_db)):
    try:
        # create new session
        new_session = create_session(db, session.session_name, session.session_id)
        return new_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))