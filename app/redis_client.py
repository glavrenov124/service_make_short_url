import os
import redis.asyncio as redis_async  
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

redis = redis_async.from_url(REDIS_URL, decode_responses=True)
