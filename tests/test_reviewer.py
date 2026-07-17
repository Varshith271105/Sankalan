from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.reviewer_service import ReviewerService

service = ReviewerService()

reviewers = service.recommend_reviewers(
    "macrocycles"
)

for reviewer, score in reviewers:
    print(reviewer, score)