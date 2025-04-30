from fastapi import APIRouter, Request
from app.models.schemas import AnswerRequest, AnswerResponse
from app.services.answer_service import generate_answer, stream_generate_answer

router = APIRouter()

@router.post("/answers", response_model=AnswerResponse, name="answers")
async def answer(endpoint_request: AnswerRequest, request: Request):
    """
    Answer endpoint router (thin).
    Delegates processing to service layer.
    """
    print(endpoint_request)
    return await generate_answer(endpoint_request, request)



router = APIRouter()

@router.post("/answer", response_model=AnswerResponse, name="answer")
async def answer_stream(endpoint_request: AnswerRequest, request: Request):
    """
    Streams response from LLM + appends function outputs.
    """
    return await stream_generate_answer(endpoint_request, request)
