from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.api.answer import router as answer_router

app = FastAPI(title="LLM Answer Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all headers
    allow_credentials=False        # MUST be False with allow_origins=["*"]
)

app.include_router(answer_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "chat.html",           # or chat.html – whichever you use
        {"request": request}
    )



@app.get("/health", response_model=None)
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)
