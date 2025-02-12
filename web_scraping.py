# web_scraping.py

import requests
from bs4 import BeautifulSoup
import chromadb
import ollama
from langchain_ollama import OllamaEmbeddings, OllamaLLM
import re
from duckduckgo_search import DDGS
import os

LLM_MODEL = "llama3.2"
CHROMA_DB_PATH = os.path.join(os.getcwd(), "chroma_db")
COLLECTION_NAME = "news_articles_collection"

# Initialize ChromaDB client and embedding function
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

embedding_function = OllamaEmbeddings(
    model=LLM_MODEL, 
    base_url="http://localhost:11434" 
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"description": "A collection for news articles"},
    embedding_function=embedding_function
)

# DuckDuckGo search function
def ddg_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
    urls = [result['href'] for result in results if 'href' in result]
    return urls

# Function to fetch page content
def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")
    return [p.get_text() for p in paragraphs]

# Truncate content to limit
def truncate(text, max_words=666):
    words = text.split()
    return " ".join(words[:max_words]) if len(words) > max_words else text


# Function to save results to ChromaDB
def save_to_chromadb(search_results, source_urls):
    if len(search_results) != len(source_urls):
        print("Warning: Mismatch in the number of search results and source URLs. Skipping invalid data.")
        return

    embeddings = embedding_function.embed_documents(search_results)
    for i, content in enumerate(search_results):
        if content:
            collection.add(
                ids=[f"doc_{i}"],
                documents=[content],
                embeddings=[embeddings[i]],
                metadatas=[{"source": source_urls[i]}]
            )


# Function to create the prompt for Ollama
def create_prompt_ollama(llm_query, search_results):
    content = "Answer the question using only the context below.\n\n" + "\n\n---\n\n".join(search_results) + f"\n\nQuestion: {llm_query}\nAnswer:"
    return [{'role': 'user', 'content': content}]

# Function to generate response from Ollama
def create_completion_ollama(prompt):
    try:
        completion = ollama.chat(model=LLM_MODEL, messages=prompt)
        return completion['message']['content'] if 'message' in completion else "Error generating response."
    except Exception as e:
        return "An error occurred while processing your request."
