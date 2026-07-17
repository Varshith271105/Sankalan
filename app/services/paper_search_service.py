from typing import List

from app.clients.semantic_scholar_client import SemanticScholarClient
from app.mappers.paper_mapper import PaperMapper
from app.models.paper import Paper


class PaperSearchService:
    """
    Business logic for paper searching.
    """

    def __init__(self):
        self.client = SemanticScholarClient()

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Paper]:

        response = self.client.search_papers(
            query=query,
            limit=limit,
        )

        papers = []

        for paper_json in response.get("data", []):

            paper = PaperMapper.from_api(
                paper_json
            )

            papers.append(paper)

        return papers