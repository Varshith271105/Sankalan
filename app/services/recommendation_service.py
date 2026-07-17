from typing import List

from app.clients.semantic_scholar_client import SemanticScholarClient
from app.mappers.paper_mapper import PaperMapper
from app.models.paper import Paper


class RecommendationService:
    """
    Business logic for retrieving recommended papers.
    """

    def __init__(self):
        self.client = SemanticScholarClient()

    def get_recommendations(
        self,
        paper_ids: list[str],
        limit: int = 10,
    ) -> List[Paper]:

        response = self.client.get_recommendations(
            paper_ids=paper_ids,
            limit=limit,
        )

        return [
            PaperMapper.from_api(paper)
            for paper in response.get("recommendedPapers", [])
        ]