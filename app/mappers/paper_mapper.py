from app.models.paper import Paper
from app.models.author import Author


class PaperMapper:
    """
    Converts Semantic Scholar API responses
    into Paper model objects.
    """

    @staticmethod
    def from_api(data: dict) -> Paper:
        """
        Convert one Semantic Scholar paper JSON
        into a Paper object.
        """

        authors = []

        for author in data.get("authors") or []:
            authors.append(
                Author(
                    author_id=author.get("authorId"),
                    name=author.get("name", "Unknown"),
                )
            )

        journal = (
            data.get("journal") or {}
        ).get("name")

        pdf_url = (
            data.get("openAccessPdf") or {}
        ).get("url")

        doi = (
            data.get("externalIds") or {}
        ).get("DOI")

        return Paper(
            paper_id=data.get("paperId") or "",
            title=data.get("title", ""),
            abstract=data.get("abstract"),
            authors=authors,
            year=data.get("year"),
            journal=journal,
            venue=data.get("venue"),
            citation_count=data.get("citationCount") or 0,
            reference_count=data.get("referenceCount") or 0,
            influential_citation_count=data.get("influentialCitationCount") or 0,
            doi=doi,
            url=data.get("url"),
            pdf_url=pdf_url,
            fields_of_study=data.get("fieldsOfStudy") or [],
        )