# Main fast API file 
# uvicorn app.main:app --reload

from fastapi import FastAPI
from .routes.file_upload import router as file_app
from .routes.qa import router as qa_app
from .routes.session import router as session_app
from contextlib import asynccontextmanager
from .database.postgres import engine
from .database.tables import Base

# Define the lifespan context manager for startup events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the sessions table when the app starts
    Base.metadata.create_all(bind=engine)
    
    # create a retriver store to store the retriever for lifetime of fast API app
    app.state.retriever_store = {}
    # # the same as above but store chat history
    app.state.chat_history = {}
    # print("Tables created successfully on startup")
    
    # Yield control to FastAPI (request handling phase)
    yield
    
    # Code here will run on shutdown
    print("Application is shutting down...")

app = FastAPI(lifespan=lifespan)
@app.get("/debug")
async def debug_state():
    return {
        "retriever_store": len(app.state.retriever_store),
        "chat_history": app.state.chat_history,
    }
app.include_router(file_app)
app.include_router(qa_app)
app.include_router(session_app)