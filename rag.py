from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Document, Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.groq import Groq
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from chromadb import PersistentClient
import os
from dotenv import load_dotenv

load_dotenv()   

chats = [] # In memory chat

def saveTOVector(string: str):
    chromadb_client = PersistentClient("./chroma_db")
    collection = chromadb_client.get_or_create_collection("news_collection")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    embedding_model = HuggingFaceEmbedding()
    parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=50)
    docs = Document(text=string)
    nodes = parser.get_nodes_from_documents([docs])

    index = VectorStoreIndex(
        nodes,
        storage_context = storage_context,
        embed_model = embedding_model
        )

    embedding_count = collection.count()
    return {
        "message": f"{string} ingested successfully. No of embeddings in db is: {embedding_count}"
    }


def saveToVectorFile(file):
    
    client = PersistentClient("./chroma_db")
    collection =client.get_or_create_collection("news_collection")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    embedding_model = HuggingFaceEmbedding()
    parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=50)
    string = file.file.read().decode("utf-8")
    docs = Document(text=string)
    nodes = parser.get_nodes_from_documents([docs])

    index = VectorStoreIndex(
        nodes,
        storage_context = storage_context,
        embed_model = embedding_model
        ) 
    embedding_count = collection.count()
    return {
        "message": f"The document ingested successfully. No of embeddings in db is: {embedding_count}"
    }

def getEmbeddings(question :str):
    cliet = PersistentClient("./chroma_db")
    collection = cliet.get_or_create_collection("news_collection")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    embedding_model = HuggingFaceEmbedding()
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context = storage_context, 
        embed_model = embedding_model
        )
    
    retriever =index.as_retriever(response_mode="simple")
    response = retriever.retrieve(question)
    return {"Question" : question,
            "Answer" : response}

def getResponse(question :str):
    Settings.llm = Groq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
    )

    cliet = PersistentClient("./chroma_db")
    collection = cliet.get_or_create_collection("news_collection")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    embedding_model = HuggingFaceEmbedding()
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context = storage_context, 
        embed_model = embedding_model
        )
    
    query_engine = index.as_query_engine()
    
    response = query_engine.query(question)
    
    return {
        "question": question,
        "answer": response.response
    }

def getResposeWithChat(question :str):
    Settings.llm = Groq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
    )

    cliet = PersistentClient("./chroma_db")
    collection = cliet.get_or_create_collection("news_collection")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    embedding_model = HuggingFaceEmbedding()
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context = storage_context, 
        embed_model = embedding_model
        )
    
    chat_history = [] 

    for chat in chats:
        role = MessageRole.USER if chat["role"] == "user" else MessageRole.ASSISTANT
        chat_history.append(ChatMessage(role=role, content=chat["content"])) 

    chat_engine = index.as_chat_engine(
        chat_mode="context",
        system_prompt="You are a concise assistant. Answer in exactly one or two short sentences based on the context."
    )

    response = chat_engine.chat(question,chat_history=chat_history)
    chats.append({"role": "user", "content": question})
    chats.append({"role": "assistant", "content": response.response})
    return {
        "question": question,
        "answer": response.response,
        "chat_history": chats
    }