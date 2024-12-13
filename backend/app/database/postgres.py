from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

postgres_url=os.getenv("POSTGRES_URL")
db_name =os.getenv("DB_NAME")

FULL_URL = f"{postgres_url}/{db_name}"

# print(DATABASE_URL)

engine = create_engine(FULL_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create the tables 
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()