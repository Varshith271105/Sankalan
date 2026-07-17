from collections import Counter

from app.services.paper_search_service import PaperSearchService


class TrendService:

    def __init__(self):
        self.search_service = PaperSearchService()

    def get_trending_topics(
        self,
        query: str,
        limit: int = 100,
    ):

        papers = self.search_service.search(
            query=query,
            limit=limit,
        )

        counter = Counter()

        for paper in papers:
            counter.update(paper.fields_of_study)

        return counter.most_common()