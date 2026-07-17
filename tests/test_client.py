from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.clients.semantic_scholar_client import SemanticScholarClient

client = SemanticScholarClient()

papers = client.search_papers(
    "Macrocycles generating",
    limit=20
)

print(papers)