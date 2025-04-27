# AskGenie (Python Version)

A modular, scalable LLM-based answer generation engine that:
- Rephrases search queries intelligently
- Searches the web (Brave / Serper)
- Scrapes webpages for context
- Applies RAG (Retrieval Augmented Generation)
- Uses real Function Calling (e.g., Maps, News, Shopping APIs)
- Generates answers and follow-up questions

Built purely in **Python + FastAPI** with production-grade enterprise architecture.

---

## 🚀 Features

- ✅ OpenAI / Groq model switching
- ✅ Function Calling Support (Real Map, News, Shopping fetches)
- ✅ Web search (Serper/Brave API based)
- ✅ Web scraping & HTML parsing
- ✅ FAISS-based RAG (Retrieval-Augmented Generation)
- ✅ Redis Caching and Rate Limiting
- ✅ Modular, extensible services
- ✅ Multi-tool chaining support (multiple function call executions!)
- ✅ Async, fast, and highly efficient

---

## 🛠 Tech Stack

- FastAPI
- LangChain
- OpenAI Python SDK
- Redis (async)
- FAISS (CPU)
- BeautifulSoup (scraping)
- Serper API (Search/News/Shopping)
- Docker (for Redis)
- Pydantic v2
- AsyncIO

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
├── services/            # Core services (search, LLM, RAG, scraper)
│   ├── answer_service.py
│   ├── llm.py
│   ├── rag.py
│   ├── scraper.py
│   ├── search.py
│   ├── search_selector.py
│   ├── functions.py     # Function calling logic
│   ├── tools.py         # Function tool definitions
│   ├── utils.py
├── cache.py             # Redis connection & semantic cache
├── main.py              # FastAPI app entrypoint
```

---

## ⚙️ Prerequisites

- Python 3.10+
- Docker (for Redis)
- OpenAI API Key or Groq API Key
- Serper API Key (for Search/News/Shopping)
- Brave API Key (optional if using Brave Search)

---

## 🛠 Installation Steps

```bash
# 1. Clone the repo
git clone https://github.com/RahulpndtRp/AskGenie.git
cd AskGenie

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Setup .env configuration
cp .env.example .env
# Fill in your API keys inside .env
```

---

## 🧹 Running the Application

### Start Redis using Docker:

```bash
docker run -d -p 6379:6379 redis
```

### Start FastAPI server:

```bash
uvicorn app.main:app --reload
```

Swagger Docs available at:  
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🖥️ Chat UI (Built-in)

A lightweight, production-grade Chat UI is also included!

- No frontend build step required
- Fully embedded using Jinja2 templates
- Supports preloaded questions, dark mode, function calling results, sources, and settings panel
- Directly integrated into FastAPI

### Access the Chat UI here:

```bash
http://localhost:8000/
```

✅ Start chatting instantly after running your FastAPI server!  
✅ You can adjust API call parameters (e.g., chunk size, sources) from the side panel settings.

---

## 📚 API Endpoint Documentation

### POST `/answer`

**Request Body Example:**

```json
{
  "message": "Find hotels near Disneyland and current weather there",
  "return_sources": true,
  "return_follow_up_questions": true,
  "embed_sources_in_llm_response": true
}
```

**Sample Response:**

```json
{
  "answer": "You can locate Disneyland using Google Maps. The current weather is sunny with a temperature of 25°C...",
  "sources": [
    {"title": "Tripadvisor Hotels near Disneyland", "link": "https://tripadvisor.com/xyz"}
  ],
  "follow_up_questions": [
    "Top attractions near Disneyland?",
    "Best restaurants around Disneyland?"
  ],
  "tool_outputs": [
    {
      "function_name": "search_location",
      "arguments": {"query": "Disneyland"},
      "response": {
        "map_url": "https://www.google.com/maps/search/?api=1&query=Disneyland",
        "query": "Disneyland"
      }
    },
    {
      "function_name": "search_news",
      "arguments": {"query": "Disneyland weather"},
      "response": {
        "title": "Weather Updates for Disneyland",
        "link": "https://weather.com/xyz"
      }
    }
  ]
}
```

---

## 🧩 Environment Variables (.env Example)

```env
# LLM Providers
llm_provider=openai
openai_api_key=your_openai_key
groq_api_key=your_groq_key

# Search APIs
search_provider=serper
serper_api_key=your_serper_key
brave_api_key=your_brave_key

# LLM Settings
answer_model=gpt-4o-mini
followup_model=gpt-4o-mini
requests_per_minute=30

# Redis Settings
redis_host=localhost
redis_port=6379
redis_db=0

# Feature Flags
use_function_calling=true
embed_sources_in_llm_response=true
```

---

## 🚀 Future Enhancements

- Add Azure OpenAI support
- Add Anthropic Claude support
- WebSocket streaming live answers
- File upload-based RAG (document search)
- Ollama local model compatibility
- Fine-grained semantic caching
- More flexible Frontend options (Chainlit)
- Memeory based Chat Profile

---

## 📜 License

MIT License.

---

## 🤝 Credits

Built with ❤️ by Rahul Pandey.

---
