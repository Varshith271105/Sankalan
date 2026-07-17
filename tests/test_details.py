from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.paper_details_service import PaperDetailsService

service = PaperDetailsService()

paper = service.get_paper(
    "09d8841eeb362a2c04f055f70f16d634093c83bc"
)

print("=" * 60)
print("Title:", paper.title)
print("Year:", paper.year)
print("Journal:", paper.journal)
print("Authors:", [a.name for a in paper.authors])