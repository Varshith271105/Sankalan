from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.trend_service import TrendService

service = TrendService()

topics = service.get_trending_topics(
    "Agentic AI"
)

for topic, count in topics:
    print(topic, count)