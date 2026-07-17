import time
from typing import Any, Dict, Optional

import requests

from app.utils.config import settings
from app.utils.constants import PAPER_FIELDS


class SemanticScholarClient:
    """
    Client responsible for communicating with the
    Semantic Scholar Graph API.
    """

    def __init__(self):
        self.graph_url = settings.GRAPH_URL
        self.recommendation_url = settings.RECOMMENDATION_URL
        self.timeout = settings.REQUEST_TIMEOUT

        self.headers = {
            "x-api-key": settings.API_KEY,
            "Accept": "application/json"
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        base_url: Optional[str] = None,
    ) -> Dict[str, Any]:

        if base_url is None:
            base_url = self.graph_url

        url = f"{base_url}/{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=json,
            timeout=self.timeout,
        )


        response.raise_for_status()

        # Respect Semantic Scholar rate limit
        time.sleep(3)

        return response.json()

    def search_papers(
        self,
        query: str,
        limit: int = settings.DEFAULT_LIMIT
    ) -> Dict[str, Any]:
        """
        Search research papers.
        """

        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join(PAPER_FIELDS),
        }

        return self._request(
            method="GET",
            endpoint="paper/search",
            params=params
        )
    
    # ----------------------------------------------------
    # PAPER DETAILS
    # ----------------------------------------------------

    def get_paper(
        self,
        paper_id: str,
    ) -> Dict[str, Any]:

        params = {
            "fields": ",".join(PAPER_FIELDS),
        }

        return self._request(
            method="GET",
            endpoint=f"paper/{paper_id}",
            params=params,
        )

    # ----------------------------------------------------
    # AUTHOR SEARCH
    # ----------------------------------------------------

    def search_authors(
        self,
        query: str,
        limit: int = 10,
    ) -> Dict[str, Any]:

        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join([
                "name",
                "paperCount",
                "citationCount",
                "hIndex",
                "affiliations",
            ])
        }

        return self._request(
            method="GET",
            endpoint="author/search",
            params=params,
        )

    # ----------------------------------------------------
    # AUTHOR DETAILS
    # ----------------------------------------------------

    def get_author(
        self,
        author_id: str,
    ) -> Dict[str, Any]:

        params = {
            "fields": ",".join([
                "name",
                "paperCount",
                "citationCount",
                "hIndex",
                "affiliations",
                "papers",
            ])
        }

        return self._request(
            method="GET",
            endpoint=f"author/{author_id}",
            params=params,
        )

    # ----------------------------------------------------
    # REFERENCES
    # ----------------------------------------------------

    def get_references(
        self,
        paper_id: str,
    ) -> Dict[str, Any]:

        reference_fields = ",".join(
            f"references.{field}"
            for field in PAPER_FIELDS
        )

        params = {
            "fields": reference_fields
        }

        return self._request(
            method="GET",
            endpoint=f"paper/{paper_id}",
            params=params,
        )

    # ----------------------------------------------------
    # CITATIONS
    # ----------------------------------------------------

    def get_citations(
        self,
        paper_id: str,
    ) -> Dict[str, Any]:

        citation_fields = ",".join(
            f"citations.{field}"
            for field in PAPER_FIELDS
        )

        params = {
            "fields": citation_fields
        }

        return self._request(
            method="GET",
            endpoint=f"paper/{paper_id}",
            params=params,
        )

    # ----------------------------------------------------
    # RECOMMENDATIONS
    # ----------------------------------------------------

    def get_recommendations(
        self,
        paper_ids: list[str],
        limit: int = 10,
    ) -> Dict[str, Any]:

        payload = {
            "positivePaperIds": paper_ids
        }

        params = {
            "limit": limit
        }

        return self._request(
            method="POST",
            endpoint="papers",
            params=params,
            json=payload,
            base_url=self.recommendation_url,
        )   