from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any


class AnswerRequest(BaseModel):
    message: str
    return_sources: bool = True
    return_follow_up_questions: bool = True
    embed_sources_in_llm_response: bool = False

    text_chunk_size: int = Field(default=1000, ge=100)
    text_chunk_overlap: int = Field(default=200, ge=0)
    number_of_similarity_results: int = Field(default=2, ge=1)
    number_of_pages_to_scan: int = Field(default=4, ge=1)

    stream: bool = False  # ✅ Add this line

class Source(BaseModel):
    title: str
    link: HttpUrl

class FunctionCallOutput(BaseModel):
    function_name: str
    arguments: dict
    response: str
    
class AnswerResponse(BaseModel):
    answer: str
    sources: Optional[List[Source]] = None
    follow_up_questions: Optional[List[str]] = None
    tool_outputs: Optional[List[Dict[str, Any]]] = None   # 🎯 Fix here
