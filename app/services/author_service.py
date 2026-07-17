from app.clients.semantic_scholar_client import SemanticScholarClient


class AuthorService:

    def __init__(self):
        self.client = SemanticScholarClient()

    def search(
        self,
        query: str,
        limit: int = 10,
    ):
        return self.client.search_authors(
            query=query,
            limit=limit,
        )

    def get(
        self,
        author_id: str,
    ):
        return self.client.get_author(author_id)