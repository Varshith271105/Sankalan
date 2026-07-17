from collections import Counter

from app.services.paper_search_service import PaperSearchService


class JournalService:
    """
    Recommends journals based on search results.
    """

    def __init__(self):
        self.search_service = PaperSearchService()

    def recommend_journals(
        self,
        query: str,
        limit: int = 100,
        top_k: int = 10,
    ):

        papers = self.search_service.search(
            query=query,
            limit=limit,
        )

        journals = [
            paper.journal
            for paper in papers
            if paper.journal
        ]

        counter = Counter(journals)

        return counter.most_common(top_k)