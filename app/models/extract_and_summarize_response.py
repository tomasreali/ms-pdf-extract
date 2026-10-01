from pydantic import BaseModel
from typing import Optional


class ExtractAndSummarizeResponse(BaseModel):
    content: str
    page_count: int
    summary: Optional[str] = None
    summary_error: Optional[str] = None
