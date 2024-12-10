from pydantic import BaseModel

class DocumentCreate(BaseModel):
    title: str
    content: str

class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True