from .crud_service import create_multi_vector_retriever
from .document_service import extract_pdf_elements, categorize_elements, relocate
from langchain_text_splitters import CharacterTextSplitter
from .summaries_service import generate_text_summaries, generate_img_summaries
from .crud_service import VectorStore

def embed_chain(fpath, fname, session_name):
    # File path
    # fpath = "sample_data/attention-is-all-you-need"
    # fname = "attention-is-all-you-need.pdf"

    # Get elements
    raw_pdf_elements = extract_pdf_elements(fpath, fname)

    # Get text, tables
    texts, tables = categorize_elements(raw_pdf_elements)

    # Optional: Enforce a specific token size for texts
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=4000, chunk_overlap=0
    )
    joined_texts = " ".join(texts)
    texts_4k_token = text_splitter.split_text(joined_texts)

    # relocate images and tables
    table_output_dir, image_output_dir = relocate(fpath=fpath,fname=fname)

    # text and table summaries
    text_summaries, table_summaries = generate_text_summaries(
        texts_4k_token, tables, summarize_texts=True
    )

    # Image summaries
    img_base64_list, image_summaries = generate_img_summaries(image_output_dir)

    vectorstore = VectorStore(collection_name=session_name)
    vectorstore.create_collection()
    qdrant = vectorstore.connect_collection()
    
    # Create retriever
    retriever_multi_vector_img = create_multi_vector_retriever(
        qdrant,
        text_summaries,
        texts,
        table_summaries,
        tables,
        image_summaries,
        img_base64_list,
    )
    return retriever_multi_vector_img