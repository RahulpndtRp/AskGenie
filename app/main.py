from fastapi import FastAPI
from app.api.answer import router as answer_router

app = FastAPI(title="LLM Answer Engine API")
app.include_router(answer_router)
