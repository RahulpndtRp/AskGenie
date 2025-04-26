
# LLM Answer Engine (Python Version)

A modular, scalable LLM-based answer generation engine that:
- Rephrases search queries intelligently
- Searches the web (Brave / Serper)
- Scrapes webpages for context
- Applies RAG (Retrieval Augmented Generation)
- Generates answers and follow-up questions

Built purely in **Python + FastAPI** with production-grade architecture.

---

## 🚀 Features

- ✅ OpenAI / Groq model switching
- ✅ Web search (Serper/Brave API based)
- ✅ Web scraping & HTML parsing
- ✅ FAISS-based RAG (Retrieval-Augmented Generation)
- ✅ Redis Caching and Rate Limiting
- ✅ Modularized, extensible services
- ✅ Async, fast, and efficient

---

## 🛠 Tech Stack

- FastAPI
- LangChain
- OpenAI Python SDK
- Redis (async)
- FAISS (CPU)
- BeautifulSoup (scraping)
- Docker (for Redis)
- Pydantic v2

---

## 📂 Folder Structure

```bash
app/
├── api/                 # FastAPI routes
│   └── answer.py
├── core/                # Config and Logger
│   ├── config.py
│   └── logger.py
├── models/              # Pydantic schemas
│   └── schemas.py
├── services/            # All core services
│   ├── answer_service.py
│   ├── llm.py
│   ├── rag.py
│   ├── scraper.py
│   ├── search.py
│   ├── search_selector.py
│   ├── utils.py
├── cache.py             # Redis connection & operations
├── main.py              # FastAPI entrypoint
```

---

## ⚙️ Prerequisites

- Python 3.10+
- Docker (for Redis)
- OpenAI API key (or Groq key)
- Brave API key (optional if using Serper)

---

## 🛠 Installation Steps

```bash
# 1. Clone the repo
git clone https://github.com/your-username/llm-answer-engine.git
cd llm-answer-engine

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# Fill your keys inside
```

---

## 🧹 Running the Application

### Run Redis using Docker:

```bash
docker run -d -p 6379:6379 redis
```

### Run FastAPI server:

```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs for Swagger UI.

---

## 📚 API Endpoint Documentation

### POST `/answer`

**Request Body:**

```json
{
  "message": "Best places to visit in Paris",
  "return_sources": true,
  "return_follow_up_questions": true,
  "embed_sources_in_llm_response": false
}
```

**Response:**

```json
{
  "answer": "Some top places in Paris are Eiffel Tower...",
  "sources": [
    {"title": "Tripadvisor - Paris", "link": "https://www.tripadvisor.com/..."},
    ...
  ],
  "follow_up_questions": [
    "What are top restaurants in Paris?",
    "Best time to visit Paris?"
  ]
}
```

---

## 🧩 Environment Variables Example (.env)

```env
# LLM
llm_provider=openai
openai_api_key=your_openai_key
groq_api_key=your_groq_key

# Search
search_provider=serper
serper_api_key=your_serper_key
brave_api_key=your_brave_key

# Settings
answer_model=gpt-3.5-turbo
followup_model=gpt-3.5-turbo
requests_per_minute=30

# Redis
redis_host=localhost
redis_port=6379
redis_db=0
```

---

## 🚀 Future Enhancements

- Add support for Azure OpenAI
- Add Anthropic Claude models
- Add Weaviate / Chroma vectorstores
- Add WebSocket streaming

---

## 📜 License

MIT License.

---

## 🤝 Credits

Built with ❤️ by Rahul Pandey.

---
