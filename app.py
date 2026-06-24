import streamlit as st
import pymupdf
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

st.set_page_config(page_title="AI Financial Research Assistant", page_icon="📚", layout="wide")

st.title("📚 AI Financial Research Assistant")
st.subheader("Upload multiple financial documents and ask questions across all of them using AI")
st.divider()

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def get_chroma_client():
    return chromadb.Client()

embedding_model = load_embedding_model()
chroma_client = get_chroma_client()

if 'collection' not in st.session_state:
    st.session_state.collection = chroma_client.get_or_create_collection(name="financial_docs")
if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def extract_text_from_pdf(pdf_file):
    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def add_document_to_db(filename, text):
    chunks = chunk_text(text)
    embeddings = embedding_model.encode(chunks).tolist()
    ids = [hashlib.md5((filename + str(i)).encode()).hexdigest() for i in range(len(chunks))]
    metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
    st.session_state.collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    return len(chunks)

def search_documents(query, n_results=5):
    query_embedding = embedding_model.encode([query]).tolist()
    results = st.session_state.collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results

def get_ai_answer(query, context_chunks, sources):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    context = "\n\n---\n\n".join([f"[From: {src}]\n{chunk}" for chunk, src in zip(context_chunks, sources)])
    prompt = "You are a financial research assistant. Answer the question using ONLY the information in the context below. If comparing documents, clearly state which document each fact comes from. If the answer is not in the context, say so clearly. Use plain text only, no LaTeX or math notation.\n\nContext:\n" + context + "\n\nQuestion: " + query + "\n\nAnswer:"
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📁 Upload Documents")
    uploaded_files = st.file_uploader("Upload PDF documents", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        for pdf_file in uploaded_files:
            if pdf_file.name not in st.session_state.uploaded_docs:
                with st.spinner(f"Processing {pdf_file.name}..."):
                    text = extract_text_from_pdf(pdf_file)
                    num_chunks = add_document_to_db(pdf_file.name, text)
                    st.session_state.uploaded_docs.append(pdf_file.name)
                    st.success(f"✅ {pdf_file.name} added! ({num_chunks} chunks indexed)")

    st.divider()
    st.markdown("### 📋 Indexed Documents")
    if st.session_state.uploaded_docs:
        for doc in st.session_state.uploaded_docs:
            st.info(f"📄 {doc}")
    else:
        st.info("No documents indexed yet")

    if st.button("🗑️ Clear All Documents"):
        chroma_client.delete_collection(name="financial_docs")
        st.session_state.collection = chroma_client.get_or_create_collection(name="financial_docs")
        st.session_state.uploaded_docs = []
        st.session_state.chat_history = []
        st.success("All documents cleared!")
        st.rerun()

with col2:
    st.markdown("### 💬 Ask Questions")

    if not st.session_state.uploaded_docs:
        st.info("👈 Upload documents first to start asking questions!")
    else:
        for q, a in st.session_state.chat_history:
            st.markdown(f"**You:** {q}")
            st.info(a)
            st.markdown("---")

        question = st.text_input("Ask a question across your documents...", placeholder="e.g. Compare the revenue growth between these documents")

        if st.button("🔍 Get Answer"):
            if question:
                with st.spinner("🔎 Searching documents and generating answer..."):
                    results = search_documents(question)
                    context_chunks = results['documents'][0]
                    sources = [meta['source'] for meta in results['metadatas'][0]]
                    answer = get_ai_answer(question, context_chunks, sources)
                    st.session_state.chat_history.append((question, answer))
                st.rerun()
            else:
                st.warning("Please enter a question!")

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.info("📄 **Multi-Document**\n\nUpload and search across multiple PDFs at once")
with col2:
    st.info("🔍 **Semantic Search**\n\nFinds relevant content by meaning, not just keywords")
with col3:
    st.info("🤖 **AI Answers**\n\nGet answers with source attribution from Llama 3.3")