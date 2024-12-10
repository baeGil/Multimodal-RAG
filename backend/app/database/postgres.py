from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

username=os.getenv("USERNAME")
password=os.getenv("PASSWORD")
hostname=os.getenv("HOST_NAME")
port=os.getenv("PORT")
db_name =os.getenv("DB_NAME")
DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{db_name}"

# print(DATABASE_URL)

engine = create_engine(DATABASE_URL)
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