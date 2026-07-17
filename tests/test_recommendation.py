from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.recommendation_service import RecommendationService

service = RecommendationService()

paper_id = "09d8841eeb362a2c04f055f70f16d634093c83bc"

papers = service.get_recommendations(
    [paper_id],
    limit=5,
)

for paper in papers:
    print("=" * 50)
    print(paper.title)