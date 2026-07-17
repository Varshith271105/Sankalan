from app.clients.semantic_scholar_client import SemanticScholarClient
from app.mappers.paper_mapper import PaperMapper
from app.models.paper import Paper


class PaperDetailsService:
    """
    Business logic for retrieving a single paper.
    """

    def __init__(self):
        self.client = SemanticScholarClient()

    def get_paper(
        self,
        paper_id: str,
    ) -> Paper:

        response = self.client.get_paper(
            paper_id=paper_id
        )

        return PaperMapper.from_api(response)