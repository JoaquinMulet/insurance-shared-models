import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is not set")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis_client() -> redis.Redis:
    """Dependency to get a Redis client."""
    return redis_client
