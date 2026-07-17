from typing import Optional
from pydantic import BaseModel


class Author(BaseModel):
    """Represents a research paper author."""

    author_id: Optional[str] = None
    name: str