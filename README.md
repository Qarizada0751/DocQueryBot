# 📚 RAG App

This project implements a Retrieval-Augmented Generation (RAG) system that integrates PDF document processing, web scraping, word cloud generation, swear word detection, and a Telegram bot for interactive querying. The system allows users to upload documents, ask queries, and get responses based on document contents, as well as scrape and query the web for relevant information.

## Features

### Swear Word Checking:
- The application scans user queries for offensive language using a predefined list of swear words. If detected, the system will prompt the user to avoid using inappropriate language.

### Document Upload & Processing:
- Users can upload PDF or TXT files. The contents of the document are added to a ChromaDB collection, enabling document-based retrieval for answering queries.

### Word Cloud Generation:
- After processing a document, the system generates a word cloud to visualize the most frequent terms in the uploaded document.

### Web Scraping:
- If no document is uploaded, the system performs web scraping by querying DuckDuckGo for the top search results. It extracts content from the top URLs and uses the results to generate a response.

### Telegram Bot:
- The bot listens to user queries and allows interaction. It can process documents, check queries for swear words, and retrieve responses based on document content or web scraping results.

## Project Structure

- app.py: Main file for the Streamlit UI and user interactions. Handles document uploads, query inputs, word cloud generation, and RAG processing.
- pdf_processing.py: Contains functions for extracting and processing text from PDF or TXT files, adding documents to ChromaDB, and running the RAG pipeline.
- web_scraping.py: Handles web scraping using DuckDuckGo search results, content extraction, and saving to ChromaDB.
- telegram_bot.py: Implements the Telegram bot logic for handling document uploads, query processing, and communication with the user.

## Installation

### Requirements

Make sure you have the following installed:

- Python 3.8+
- Required libraries:
  - streamlit
  - wordcloud
  - matplotlib
  - requests
  - beautifulsoup4
  - chromadb
  - langchain_ollama
  - duckduckgo-search
  - python-telegram-bot
  - ollama

You can install the required dependencies using pip:

```bash
pip install -r requirements.txt
