from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.citation_service import CitationService

service = CitationService()

paper_id = "09d8841eeb362a2c04f055f70f16d634093c83bc"

references = service.get_references(paper_id)

print("\nREFERENCES\n")

for paper in references[:5]:
    print(paper.title)

print("\n" + "=" * 60 + "\n")

citations = service.get_citations(paper_id)

print("CITATIONS\n")

for paper in citations[:5]:
    print(paper.title)