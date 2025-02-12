import logging
import io
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from pdf_processing import extract_documents, add_documents_to_chromadb, rag_pipeline, collection
from web_scraping import ddg_search, get_page, save_to_chromadb, truncate, create_prompt_ollama, create_completion_ollama
from app import contains_swear_words

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the bot's token from BotFather
TELEGRAM_API_TOKEN = 'YOUR_TOKEN_KEY'

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Send me a query or upload a document.")

async def handle_document(update: Update, context: CallbackContext):
    file = update.message.document
    file_id = file.file_id

    new_file = await context.bot.get_file(file_id)

    file_data = await new_file.download_as_bytearray() 
    file_data_io = io.BytesIO(file_data)
    file_type = file.file_name.split('.')[-1].lower()

    if file_type in ['pdf', 'txt']:

        documents = extract_documents(file_data_io, file_type)
        context.user_data['documents'] = documents

        add_documents_to_chromadb(documents, collection)

        await update.message.reply_text(f"Document uploaded and added to the database!")
        
        context.user_data['document_uploaded'] = True
    else:
        await update.message.reply_text("Please upload a PDF or TXT file.")

async def handle_query(update: Update, context: CallbackContext):
    query = update.message.text

    if contains_swear_words(query):
        await update.message.reply_text("Please refrain from using offensive language.")
        return

    await update.message.reply_text("Processing your query...")

    if context.user_data.get("document_uploaded", False):

        response = rag_pipeline(query)
        await update.message.reply_text(f"Answer to your query from the document: {response}")
    else:
        top_urls = ddg_search(query)
        docs = []
        
        for url in top_urls:
            page_content = get_page(url)

            print(f"Scraped content from {url}:")
            print(page_content)
            docs.append(page_content)
            
            if page_content:
                cleaned_content = [truncate(content) for content in page_content]
                docs.append(cleaned_content)

                print(f"Cleaned content from {url}:")
                for content in cleaned_content:
                    print(content)

        flat_docs = [item for sublist in docs for item in sublist]
        save_to_chromadb(flat_docs, top_urls)

        prompt = create_prompt_ollama(query, flat_docs)
        response = create_completion_ollama(prompt)

        await update.message.reply_text(response)

async def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))  
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))  

    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()
