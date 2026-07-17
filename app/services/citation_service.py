from typing import List

from app.clients.semantic_scholar_client import SemanticScholarClient
from app.mappers.paper_mapper import PaperMapper
from app.models.paper import Paper


class CitationService:
    """
    Business logic for retrieving citations and references.
    """

    def __init__(self):
        self.client = SemanticScholarClient()

    def get_references(
        self,
        paper_id: str,
    ) -> List[Paper]:

        response = self.client.get_references(
            paper_id
        )

        return [
            PaperMapper.from_api(reference)
            for reference in response.get("references", [])
        ]

    def get_citations(
        self,
        paper_id: str,
    ) -> List[Paper]:

        response = self.client.get_citations(
            paper_id
        )
        print(response.get("citations"))
        return [
            PaperMapper.from_api(citation)
            for citation in response.get("citations", [])
        ]