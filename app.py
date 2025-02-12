# app.py

import streamlit as st
from wordcloud import WordCloud
import  matplotlib.pyplot as plt
import re
from web_scraping import ddg_search, get_page, save_to_chromadb, truncate, create_prompt_ollama, create_completion_ollama
from pdf_processing import extract_documents, add_documents_to_chromadb, query_chromadb, query_ollama, collection, rag_pipeline


# Streamlit UI setup
st.set_page_config(page_title="📚 RAG App", layout="centered")
st.markdown("<h1 class='title'>📚 RAG App</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='subheader'>Upload a document to get started or enter a query.</h3>", unsafe_allow_html=True)

if 'previous_query' not in st.session_state:
    st.session_state.previous_query = None

if st.button("Reset Short-Term Memory"):
    st.session_state.previous_query = None
    st.success("Short-term memory reset.")

if 'previous_query' in st.session_state:
    st.write(f"Short-term memory: {st.session_state.previous_query}")


# File upload and processing
uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"], key="file_uploader")
query = st.text_input("Enter your query", key="query_input")

st.markdown('<div class="emoji">🔍</div>', unsafe_allow_html=True)

SWAY_WORDS = [
    "fuck", "shit", "bitch", "asshole", "dick", "pussy", "cunt", "bastard", "damn", "hell", 
    "douche", "slut", "whore", "fag", "faggot", "queer", "retard", "moron", "idiot", "bimbo", 
    "cock", "motherfucker", "sonofabitch", "twat", "prick", "nigger", "chink", "spic", "gook", 
    "kike", "slanteye", "paki", "wetback", "crackhead", "junkie"
]

def contains_swear_words(query):
    query_lower = query.lower()  
    for word in SWAY_WORDS:
        if word in query_lower:
            return True
    return False

# Function to generate word cloud from text
def generate_word_cloud(documents):
    all_text = " ".join([doc.page_content for doc in documents])
    
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)


if uploaded_file:
    # Process the PDF file
    file_type = uploaded_file.type.split("/")[-1]
    documents = extract_documents(uploaded_file, file_type)

    if documents:
        add_documents_to_chromadb(documents, collection)
        st.success("File content added to ChromaDB!")
    
        st.write("### Word Cloud from Uploaded Document:")
        generate_word_cloud(documents)

if query:
    st.session_state.previous_query = query

    if contains_swear_words(query):
        st.error("This content may violate our policy rights. Please refrain from using offensive language.")
    else:
        with st.spinner('Processing your query...'):
            if uploaded_file:
                response = rag_pipeline(query)

                st.chat_message("assistant").write(response)

            else:
                # Web scraping if no file uploaded
                top_urls = ddg_search(query)
                docs = []
                for url in top_urls:
                    page_content = get_page(url)
                    docs.append(page_content)
                    
                    if page_content:
                        cleaned_content = [truncate(re.sub("\n\n+", "\n", doc)) for doc in page_content]
                        docs.append(cleaned_content)
                    else:
                        print(f"Skipping URL {url} due to an error in retrieving content.")


                flat_docs = [item for sublist in docs for item in sublist]
                # Display Retrieved Data
                st.write("### Scraped Data from Retrieved URLs:")
                for idx, url in enumerate(top_urls):
                    with st.expander(f"Content from: {url}"):
                        if idx < len(docs): 
                            st.write("\n\n".join(docs[idx]))  
                        else:
                            st.write("No content retrieved.")
                
                save_to_chromadb(flat_docs, top_urls)

                 # Generate and display a word cloud from the scraped data
                st.write("### Word Cloud from Scraped Data:")
                generate_word_cloud(flat_docs)

                prompt = create_prompt_ollama(query, flat_docs)
                response = create_completion_ollama(prompt)

                st.write("### Ollama AI Response:")
                st.write(response)

if st.session_state.previous_query:
    st.write(f"### Current Query: {st.session_state.previous_query}")