from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.journal_service import JournalService

service = JournalService()

journals = service.recommend_journals(
    "macrocycles generation"
)

for journal, count in journals:
    print(journal, count)