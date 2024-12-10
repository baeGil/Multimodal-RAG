from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import getpass, os
from langchain_google_genai import ChatGoogleGenerativeAI

# embedding model
model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embed_model = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

# gemini model
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
    
gemini_model = ChatGoogleGenerativeAI( 
    model="gemini-1.5-flash",
    temperature=0,
)