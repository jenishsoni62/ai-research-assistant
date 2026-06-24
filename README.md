# 📚 AI Financial Research Assistant

A RAG (Retrieval Augmented Generation) system for querying multiple financial documents at once. Upload several PDFs and ask questions that span across all of them — the system retrieves relevant content by semantic meaning (not just keywords) and generates sourced, comparative answers.

## How It Works
1. Documents are chunked and converted into embeddings using `sentence-transformers`
2. Embeddings are stored in a local ChromaDB vector database
3. On query, the most semantically relevant chunks are retrieved across all documents
4. Groq (Llama 3.3) generates a sourced answer using only the retrieved context

## Tech Stack
Python, Streamlit, ChromaDB, sentence-transformers, Groq (Llama 3.3), PyMuPDF

## How to Run
1. `pip install streamlit groq python-dotenv pymupdf chromadb sentence-transformers`
2. Add your Groq API key to `.env`: `GROQ_API_KEY=your_key`
3. `streamlit run app.py`

## Author
Jenish Soni — BTech AI & Data Science
