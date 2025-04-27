from fastapi import APIRouter, Request
from app.models.schemas import AnswerRequest, AnswerResponse
from app.services.answer_service import generate_answer

router = APIRouter()

@router.post("/answer", response_model=AnswerResponse, name="answer")
async def answer(endpoint_request: AnswerRequest, request: Request):
    """
    Answer endpoint router (thin).
    Delegates processing to service layer.
    """
    return await generate_answer(endpoint_request, request)
