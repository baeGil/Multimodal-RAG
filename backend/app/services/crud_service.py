import uuid, os, shutil
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_core.documents import Document
from ..database.qdrant import client,collection_config
import numpy as np
from sqlalchemy.orm import Session
from ..database.tables import Session as DB
from datetime import datetime
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from .model_service import embed_model
from sqlalchemy.orm.attributes import flag_modified

def create_multi_vector_retriever(
    vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, images
):
    """
    Create retriever that indexes summaries, but returns raw images or texts
    """

    # Initialize the storage layer
    store = InMemoryStore()
    id_key = "doc_id"

    # Create the multi-vector retriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )

    # Helper function to add documents to the vectorstore and docstore
    def add_documents(retriever, doc_summaries, doc_contents):
        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [
            Document(page_content=s, metadata={id_key: doc_ids[i]})
            for i, s in enumerate(doc_summaries)
        ]
        retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(doc_ids, doc_contents)))

    # Add texts, tables, and images
    # Check that text_summaries is not empty before adding
    if text_summaries:
        add_documents(retriever, text_summaries, texts)
    # Check that table_summaries is not empty before adding
    if table_summaries:
        add_documents(retriever, table_summaries, tables)
    # Check that image_summaries is not empty before adding
    if image_summaries:
        add_documents(retriever, image_summaries, images)

    return retriever

# CRUD for qdrant vector store
class VectorStore:
    def __init__(self, collection_name):
        self.client = client
        self.collection_name = collection_name
        
    def create_collection(self): # create new collection
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=collection_config
        )

    def add_document(self, doc_id: str, vector: np.array, metadata: dict):
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{
                'id': doc_id,
                'vector': vector,
                'payload': metadata
            }]
        )
    
    def connect_collection(self):
        qdrant = QdrantVectorStore(
            embedding=embed_model,
            client=client,
            collection_name=self.collection_name,
            retrieval_mode=RetrievalMode.DENSE,
            )
        return qdrant

    def search(self, query_vector: np.array, top_k: int = 5):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            top=top_k
        )
        return results
    
    def delete(self): # delete collection
        self.client.delete_collection(
            collection_name=self.collection_name)
    
    def close(self): # close client down
        self.client.close()

# Tạo thư mục gốc nếu chưa tồn tại
def get_session_folder(session_name):
    BASE_FOLDER = "data"
    os.makedirs(BASE_FOLDER, exist_ok=True)
    """Lấy đường dẫn thư mục của phiên hội thoại."""
    return os.path.join(BASE_FOLDER, session_name)

# Create and delete folder/session 
class Directory:
    def __init__(self,uploaded_file,session_name):
        self.uploaded_file = uploaded_file
        self.session_name = session_name

    async def save_uploaded_file(self):
        """Lưu file tải lên vào thư mục tương ứng với phiên."""
        folder_name = os.path.splitext(self.uploaded_file.filename)[0]  # Tên file không có đuôi
        session_folder = get_session_folder(self.session_name) # data/session_1..
        file_folder = os.path.join(session_folder, folder_name) # data/session_1/abc
        os.makedirs(file_folder, exist_ok=True)
        file_name = self.uploaded_file.filename # abc.pdf

        file_path = os.path.join(file_folder, file_name) # data/session_1/abc/abc.pdf
        # Read the content of the file asynchronously
        content = await self.uploaded_file.read()
        # Open the file in write-binary mode and write the content
        with open(file_path, "wb") as f:
            f.write(content)
        # with open(file_path, "wb") as f:
        #     f.write(await self.uploaded_file.read())
        return file_folder, file_name, file_path
    
    def delete_session(self):
        """Xoá toàn bộ thư mục của phiên hội thoại"""
        session_folder = get_session_folder(self.session_name)
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
            
# delete pdf folder when user choose to upload another pdf file
def delete_uploaded_file(file_folder):
    """Xoá toàn bộ thư mục của file đã tải lên."""
    if os.path.exists(file_folder):
        shutil.rmtree(file_folder)

# CRUD with conversation data in postgres
# Create a new session
def create_session(db: Session, session_name: str, session_id: uuid.UUID):
    db_session = DB(
        id=session_id,
        session_name=session_name,
        conversation=[],  # Empty initial conversation
        document_path=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# Get session by ID
def get_session_by_id(db: Session, session_id: uuid.UUID):
    return db.query(DB).filter(DB.id == session_id).first()

# Delete session by ID (and related data)
def delete_session(db: Session, session_id: uuid.UUID):
    session = db.query(DB).filter(DB.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
    return session

# Update the conversation of a session
def update_conversation(db: Session, session_id: uuid.UUID, question: str, answer: str):
    # Lấy session từ cơ sở dữ liệu
    session = db.query(DB).filter(DB.id == session_id).first()
    if session:
        # Kiểm tra và khởi tạo conversation nếu chưa có
        if session.conversation is None:
            session.conversation = []
        # Thêm câu hỏi và câu trả lời vào conversation
        session.conversation.append({"question": question, "answer": answer})
        # notice SQLAlchemy that there is a change in conversation field
        flag_modified(session,"conversation")
        # Cập nhật thời gian sửa đổi
        session.updated_at = datetime.now()
        # Commit và làm mới session
        db.commit()
        db.refresh(session) 
    return session

# Add a document path to the session
def update_document_path(db: Session, session_id: uuid.UUID, document_path: str):
    session = db.query(DB).filter(DB.id == session_id).first()
    if session:
        session.document_path = document_path
        session.updated_at = datetime.now()
        db.commit()
        db.refresh(session)
    return session