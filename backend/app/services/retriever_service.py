from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableSequence
from langchain_core.prompts import MessagesPlaceholder
from .model_service import gemini_model
from langchain_core.output_parsers import StrOutputParser
from .image_service import looks_like_base64, is_image_data, resize_base64_image

# Adding memory
# Question maker

instruction_to_system = """
Given a chat history and the latest user question 
which might reference context in the chat history, formulate a standalone question 
which can be understood without the chat history. Do NOT answer the question, 
just reformulate it if needed and otherwise return it as is.
"""
def question_chain(prompt):
    question_maker_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    # return question_maker_prompt | gemini_model | StrOutputParser()
    return RunnableSequence(question_maker_prompt, gemini_model, StrOutputParser())

# Choose the question to pass to the LLM
def contextualized_question(input: dict):
    if input.get("chat_history"):
        return question_chain(instruction_to_system)
    else:
        return input["question"]

def split_image_text_types(docs):
    """
    Split base64-encoded images and texts
    """
    b64_images = []
    texts = []
    for doc in docs:
        # Check if the document is of type Document and extract page_content if so
        if isinstance(doc, Document):
            doc = doc.page_content
        if looks_like_base64(doc) and is_image_data(doc):
            doc = resize_base64_image(doc, size=(1300, 600))
            b64_images.append(doc)
        else:
            texts.append(doc)
    return {"images": b64_images, "texts": texts}

def img_prompt_func(data_dict):
    """
    Join the context into a single string
    """
    formatted_texts = "\n".join(data_dict["context"]["texts"])
    messages = []

    # Adding image(s) to the messages if present
    if data_dict["context"]["images"]:
        for image in data_dict["context"]["images"]:
            image_message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
            }
            messages.append(image_message)

    # Adding the text for q and a
    text_message = {
        "type": "text",
        "text": (
            "You are a helpful and smart math assistant tasking with providing mathematics knowledge \n"
            "You will be given a mixed of text, tables, and image(s) usually of charts or graphs.\n"
            "Use this information to provide the answer to the user question.\n"
            "The answer must ONLY be written in LaTeX format (or HTML if needed).\n"
            "Only provide meaningful, complete and concise answer. If you don't know the answer, just say you don't know, dont' try to make up one.\n"
            f"User-provided question: {data_dict['question']}\n\n"
            "Text and / or tables:\n"
            f"{formatted_texts}"
        ),
    }
    messages.append(text_message)
    system_prompt = "Your name is Gilgamesh"
    
    qa_prompt = ChatPromptTemplate.from_messages(
    [   SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessage(content=messages)
    ]
)
    return qa_prompt

def multi_modal_rag_chain(retriever):
    """
    Multi-modal RAG chain
    """
    context_chain = RunnableSequence(contextualized_question, retriever, RunnableLambda(split_image_text_types))
    # RAG pipeline with conversational memory
    chain =RunnableSequence(
        RunnablePassthrough.assign(context = context_chain), RunnableLambda(img_prompt_func), gemini_model, StrOutputParser()
    )
    return chain

def qa_chain(question, retriever, chat_history):
    # Create RAG chain
    chain_multimodal_rag = multi_modal_rag_chain(retriever)
    # get the answer
    answer = chain_multimodal_rag.invoke({"question": question, "chat_history": chat_history})
    # add the q-a pair to chat history
    chat_history.extend([
    HumanMessage(content=question),
    AIMessage(content=answer)
    ]) # add conversation to chat_history
    return str(answer)