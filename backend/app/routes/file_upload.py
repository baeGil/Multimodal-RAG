from fastapi import Depends, HTTPException, Form, UploadFile, File, Request
import uuid
from sqlalchemy.orm import Session
from ..services.embed_service import embed_chain
from ..services.crud_service import Directory, update_document_path
from ..database.postgres import get_db
# from .shared_state import get_retriever_store
from fastapi import APIRouter
from pydantic import BaseModel, Json
from typing import Annotated

router = APIRouter()

class SessionInfo(BaseModel):
    session_id: uuid.UUID
    session_name: str
    
# Upload the file
@router.post("/file/upload/")
async def embed_file(
    request: Request,
    session: Annotated[Json[SessionInfo], Form(...)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        uploaded_file = Directory(file, session.session_name)
        folder_path, fname, file_path = await uploaded_file.save_uploaded_file() # save the uploaded file to local
        store = request.app.state.retriever_store # get the retriever store 
        history = request.app.state.chat_history # get the chat history 
        # Call the embedding function
        retriever = embed_chain(folder_path, fname, session.session_name)

        # Store the doc path in postgres
        update_document_path(db, session.session_id, file_path)

        # Store retriever
        retriever_data = {
		    "retriever": retriever,
		    "session name": session.session_name,
		    "type": type(retriever).__name__
            }
        # create retriever data for specific session id 
        store[session.session_id] = retriever_data
        
        # create chat history data
        chat_data = {
		    "chat history": [],
		    "session name": session.session_name
	        }
        # create chat history if not exist 
        if session.session_id not in history:
            history[session.session_id] = chat_data
            
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))