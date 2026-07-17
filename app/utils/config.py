from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()


class Settings:
    """Application configuration."""

    # Semantic Scholar
    API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    GRAPH_URL = os.getenv(
    "SEMANTIC_SCHOLAR_GRAPH_URL",
    "https://api.semanticscholar.org/graph/v1",
    )

    RECOMMENDATION_URL = os.getenv(
        "SEMANTIC_SCHOLAR_RECOMMENDATION_URL",
        "https://api.semanticscholar.org/recommendations/v1",
    )

    # Defaults
    DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", 10))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    


# Single settings object used throughout the project
settings = Settings()