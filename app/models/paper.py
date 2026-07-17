from typing import List, Optional

from pydantic import BaseModel, Field
from app.models.author import Author

class Paper(BaseModel):
    """Represents a research paper."""

    paper_id: str = Field(..., description="Semantic Scholar Paper ID")

    title: str

    abstract: Optional[str] = None

    authors: List[Author] = []

    year: Optional[int] = None

    journal: Optional[str] = None

    venue: Optional[str] = None

    citation_count: int = 0

    reference_count: int = 0

    influential_citation_count: int = 0

    doi: Optional[str] = None

    url: Optional[str] = None

    pdf_url: Optional[str] = None

    fields_of_study: List[str] = []