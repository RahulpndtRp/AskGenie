# app/services/embedding_service.py

from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_mistralai import MistralAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.config import settings
from app.core.logger import logger

class EmbeddingService:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.embedder = self._configure_embedder()

    def _configure_embedder(self):
        """
        Dynamically configure embedder based on settings.
        """
        provider = settings.llm_provider.lower()

        if provider == "openai" or provider == "groq":
            logger.info("[Embedder] Using OpenAI Embeddings.")
            return OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key
            )
        elif provider == "groq":
            logger.info("[Embedder] Using Groq (OpenAI-Compatible) Embeddings.")
            return OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.groq_api_key,
                openai_api_base="https://api.groq.com/openai/v1"
            )
        elif provider == "mistral":
            logger.info("[Embedder] Using MistralAI Embeddings.")
            return MistralAIEmbeddings(
                model=settings.embedding_model,  # like "mistral-embed"
                mistral_api_key=settings.mistral_api_key
            )
        elif provider == "ollama":
            logger.info("[Embedder] Using HuggingFace Embeddings (for Ollama).")
            return HuggingFaceEmbeddings(
                model_name=settings.embedding_model
            )
        elif provider == "cohere":
            logger.info("[Embedder] Using Cohere Embeddings.")
            return CohereEmbeddings(
            model=settings.embedding_model,  # Example: "embed-english-v3"
            cohere_api_key=settings.cohere_api_key
        )
        else:
            logger.error(f"[Embedder] Unknown embedding provider: {provider}")
            raise ValueError(f"Unsupported embedding provider: {provider}")

    def _sanitize_texts(self, texts: List) -> List[str]:
        """
        Clean the list of texts:
        - Keep only valid non-empty strings
        - Remove leading/trailing whitespace
        - Auto-convert simple non-str types to str if needed
        """
        if not isinstance(texts, list):
            raise ValueError("Input must be a list.")

        cleaned = []
        for text in texts:
            if isinstance(text, str):
                stripped = text.strip()
                if stripped:
                    cleaned.append(stripped)
            elif text is not None:
                stripped = str(text).strip()
                if stripped:
                    cleaned.append(stripped)

        if not cleaned:
            raise ValueError("[Sanitizer] No valid non-empty strings found after sanitization.")

        logger.info(f"[Sanitizer] Cleaned {len(texts)} -> {len(cleaned)} valid text chunks.")
        return cleaned


    def chunk_and_embed(self, texts: List[str], metadatas: List[dict] = None) -> FAISS:
        """
        Split texts into chunks, sanitize, embed, and return FAISS vectorstore.
        """
        try:
            logger.info(f"[Embedder] Starting chunking and embedding of {len(texts)} documents.")

            # 🛡️ Step 1: Clean initial texts before splitting
            texts = self._sanitize_texts(texts)

            all_chunks, all_meta = [], []
            for idx, text in enumerate(texts):
                chunks = self.splitter.split_text(text)
                meta = (metadatas[idx] if metadatas and idx < len(metadatas) else {})
                for c in chunks:
                    all_chunks.append(c)
                    all_meta.append(meta)

            # 🛡️ Step 2: Clean chunks before embedding
            all_chunks = self._sanitize_texts(all_chunks)

            store = FAISS.from_texts(
                all_chunks,
                embedding=self.embedder,
                metadatas=all_meta
            )
            logger.info(f"[Embedder] Successfully embedded {len(all_chunks)} chunks.")
            return store
        except Exception as e:
            logger.error(f"[Embedder] Error during chunking and embedding: {e}")
            raise


    def similarity_search(self, store: FAISS, query: str, k: int = 2) -> List[Dict]:
        """
        Search vectorstore for similar chunks.
        """
        try:
            logger.info(f"[Embedder] Running similarity search for query: {query}")
            docs = store.similarity_search(query, k=k)
            results = [{"text": doc.page_content, **doc.metadata} for doc in docs]
            logger.info(f"[Embedder] Found {len(results)} similar documents.")
            return results
        except Exception as e:
            logger.error(f"[Embedder] Error during similarity search: {e}")
            raise

# ✅ Instantiate once
embedding_service = EmbeddingService()
