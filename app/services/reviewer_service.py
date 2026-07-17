from collections import defaultdict

from app.services.paper_search_service import PaperSearchService


class ReviewerService:

    def __init__(self):
        self.search_service = PaperSearchService()

    def recommend_reviewers(
        self,
        query: str,
        limit: int = 100,
        top_k: int = 10,
    ):

        papers = self.search_service.search(
            query=query,
            limit=limit,
        )

        reviewers = defaultdict(int)

        for paper in papers:
            for author in paper.authors:
                reviewers[author.name] += paper.citation_count

        return sorted(
            reviewers.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]