from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.paper_search_service import PaperSearchService

service = PaperSearchService()

papers = service.search(
    "Agentic AI",
    limit=3,
)

for paper in papers:
    print("=" * 60)
    print("Title :", paper.title)
    print("Year :", paper.year)
    print("Journal :", paper.journal)
    print("Citations :", paper.citation_count)
    print("Authors :", [a.name for a in paper.authors])