# pdf_processing.py

import os
import tempfile
import streamlit as st
import chromadb
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader

LLM_MODEL = "llama3.2"
CHROMA_DB_PATH = os.path.join(os.getcwd(), "chroma_db")
COLLECTION_NAME = "rag_collection_demo"

# Initialize ChromaDB client and embedding function
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Custom embedding function
class ChromaDBEmbeddingFunction:
    def __init__(self, langchain_embeddings):
        self.langchain_embeddings = langchain_embeddings

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        return self.langchain_embeddings.embed_documents(input)

# Initialize embedding function
embedding_function = ChromaDBEmbeddingFunction(
    OllamaEmbeddings(
        model=LLM_MODEL,
        base_url="http://localhost:11434"  # Adjust if Ollama runs elsewhere
    )
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"description": "A collection for RAG with Ollama"},
    embedding_function=embedding_function
)

# Extract documents from PDF or TXT file
def extract_documents(uploaded_file, file_type):

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())  # Write the content of the BytesIO object to the temp file
        temp_path = temp_file.name

    try:

        if file_type == "pdf":
            loader = PyPDFLoader(temp_path)  # Load PDF
        elif file_type == "txt":
            loader = TextLoader(temp_path)  # Load TXT
        else:
            raise ValueError("Unsupported file type")

        documents = loader.load()
    finally:
        os.unlink(temp_path)

    return documents

# Function to add documents to ChromaDB
def add_documents_to_chromadb(documents, collection):
    text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=128)
    text_chunks = text_splitter.split_documents(documents)

    current_id = len(collection.get()["documents"])

    for i, chunk in enumerate(text_chunks):
        if hasattr(chunk, "page_content"):
            content = chunk.page_content
        elif isinstance(chunk, str):
            content = chunk
        else:
            st.error(f"Unexpected chunk format: {chunk}")
            raise ValueError("Unexpected document chunk format")

        collection.add(
            documents=[content],
            ids=[f"doc_{current_id + i}"],
            metadatas=[getattr(chunk, "metadata", {})]
        )

# Query ChromaDB for relevant documents
def query_chromadb(query_text, n_results=5):
    results = collection.query(query_texts=[query_text], n_results=n_results)
    return results["documents"], results["metadatas"]

# Query Ollama for answers
def query_ollama(prompt):
    llm = OllamaLLM(model=LLM_MODEL)
    return llm.invoke(prompt)

# RAG pipeline
def rag_pipeline(query_text):
    # Retrieve documents from ChromaDB
    retrieved_docs, metadatas = query_chromadb(query_text)
    
    if not retrieved_docs or not any(doc.strip() for doc in retrieved_docs[0]):
        return "No relevant documents were found in the collection to answer your query."

    context = " ".join(retrieved_docs[0])

    print("Context retrieved from ChromaDB:")
    print(context)
    
    if len(context.split()) < 20: 
        non_relative_message = "The following documents were retrieved, but they may not be relevant to your query:\n\n"
        for i, doc in enumerate(retrieved_docs[0]):
            non_relative_message += f"Document {i + 1}:\n{doc}\n\n"
        return non_relative_message

    # Construct the augmented prompt for the LLM
    augmented_prompt = f"""
    You are a document-based assistant. Answer to the question based on the provided context.
    Context: {context}

    Question: {query_text}
    Answer:
    """
    # Query the LLM
    response = query_ollama(augmented_prompt)
    
    return response
