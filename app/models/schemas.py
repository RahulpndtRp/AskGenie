from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class AnswerRequest(BaseModel):
    message: str
    return_sources: bool = True
    return_follow_up_questions: bool = True
    embed_sources_in_llm_response: bool = False
    text_chunk_size: Optional[int] = 1000
    text_chunk_overlap: Optional[int] = 200
    number_of_similarity_results: Optional[int] = 2
    number_of_pages_to_scan: Optional[int] = 4

class Source(BaseModel):
    title: str
    link: HttpUrl

class AnswerResponse(BaseModel):
    answer: str
    sources: Optional[List[Source]] = None
    follow_up_questions: Optional[List[str]] = None
