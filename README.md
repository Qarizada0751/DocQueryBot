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
    ```

## Running the App
---------------

### Start the Streamlit UI:

To run the Streamlit application, use:

    ```bash
    streamlit run app.py
    ```

### Start the Telegram Bot:

To launch the Telegram bot, run:

    ```bash
    python telegram_bot.py
    ``` `

Make sure to replace YOUR\_TOKEN\_KEY in the bot code with your actual Telegram bot token from BotFather.

How It Works
------------

### Swear Word Detection

*   The system checks user queries for offensive language. If a swear word is found in the query, the system will return a polite message asking the user to refrain from using inappropriate language.
    

### PDF and TXT Document Processing

*   When a document is uploaded, it is parsed, and its text is split into smaller chunks. These chunks are then added to ChromaDB for future retrieval.
    
    *   The document is processed using the PyPDFLoader or TextLoader depending on the file type.
        
    *   Chunks of text are embedded and stored in a ChromaDB collection for efficient retrieval during query processing.
        

### Word Cloud Generation

*   The application generates a word cloud based on the text content of the uploaded document or the scraped web data. This visualizes the most common terms in the content.
    

### Web Scraping

*   If no document is uploaded, the system queries DuckDuckGo to search for relevant information based on the user's query. The top search results are scraped for text, which is then processed and stored in ChromaDB.
    
    *   The system fetches the top URLs from DuckDuckGo search results.
        
    *   Scraped content from the pages is processed, cleaned, and stored.
        
    *   Word clouds are also generated from the scraped content.
        

### Telegram Bot Integration

*   The Telegram bot allows users to:
    
    *   Upload PDF or TXT documents.
        
    *   Send queries for document-based responses.
        
    *   Trigger web scraping if no document is uploaded.
        
    *   The bot checks if the document has been uploaded or if the user query triggers web scraping.
        

### RAG Pipeline

1.  **Retrieval**: The system retrieves the most relevant documents from the ChromaDB collection based on the user's query.
    
2.  **Augmented Generation**: After retrieving the documents, the system constructs an augmented prompt that combines the context (documents) with the user's query, and generates a response using the Ollama language model.
    

Error Handling
--------------

*   The app is built to handle errors gracefully:
    
    *   If no relevant documents are found, the system returns a message indicating that no relevant information was found.
        
    *   If there is a problem with scraping or document processing, the system will notify the user accordingly.
        

How to Contribute
-----------------

1.  Fork the repository and clone it to your local machine.
    
2.  Make changes or add new features.
    
3.  Push your changes to your fork.
    
4.  Open a Pull Request to the main repository with a detailed description of your changes.
    

Issues
------

If you encounter any issues, feel free to open an issue.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Example Usage
-------------

### Uploading a Document

1.  Click on "Upload Document" in the Streamlit interface.
    
2.  Upload a PDF or TXT file.
    
3.  The document content is extracted and added to the database.
    
4.  A word cloud is generated based on the document's content.
    

### Asking a Question

1.  Enter a query in the Streamlit interface or through the Telegram Bot.
    
2.  The system will either respond based on the uploaded document or perform web scraping if no document is available.
    

Troubleshooting
---------------

### Problem: The word cloud doesn't generate.

*   **Solution**: Ensure that the document is uploaded successfully, and the text content is correctly extracted.
    

### Problem: The Telegram bot doesn't respond.

*   **Solution**: Make sure your Telegram bot token is correct and that the bot is running without errors.
    

### Problem: Web scraping is not fetching content.

*   **Solution**: Ensure that DuckDuckGo search results return valid URLs and that the requests library is able to fetch the content.
