

import aioredis
import httpx
from aioredis.exceptions import ResponseError

from config.config import *

config = Config()

redis = aioredis.from_url(config.redis_url, decode_responses=True)






