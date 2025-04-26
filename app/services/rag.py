from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.config import settings
from app.core.logger import logger

# Splitter and Embedder config
_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
_EMBEDDER = OpenAIEmbeddings(
    model=settings.embedding_model,
    openai_api_key=(
        settings.openai_api_key
        if settings.llm_provider == "openai"
        else settings.groq_api_key
    )
)

def chunk_and_embed(texts: List[str], metadatas: List[dict] = None) -> FAISS:
    """
    Split texts into chunks, embed, and return FAISS vectorstore.
    Logs each stage.
    """
    try:
        logger.info(f"[RAG] Starting chunking and embedding of {len(texts)} documents.")
        all_chunks, all_meta = [], []
        for idx, text in enumerate(texts):
            chunks = _SPLITTER.split_text(text)
            meta = (metadatas[idx] if metadatas and idx < len(metadatas) else {})
            for c in chunks:
                all_chunks.append(c)
                all_meta.append(meta)

        store = FAISS.from_texts(
            all_chunks,
            embedding=_EMBEDDER,
            metadatas=all_meta
        )
        logger.info(f"[RAG] Successfully embedded {len(all_chunks)} chunks.")
        return store
    except Exception as e:
        logger.error(f"[RAG] Error during chunking and embedding: {e}")
        raise

def similarity_search(store: FAISS, query: str, k: int = 2) -> List[Dict]:
    """
    Search vectorstore for similar chunks.
    """
    try:
        logger.info(f"[RAG] Running similarity search for query: {query}")
        docs = store.similarity_search(query, k=k)
        results = [{"text": doc.page_content, **doc.metadata} for doc in docs]
        logger.info(f"[RAG] Found {len(results)} similar documents.")
        return results
    except Exception as e:
        logger.error(f"[RAG] Error during similarity search: {e}")
        raise
