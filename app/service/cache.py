
import json

from datetime import datetime

from service.keys import *

from utils.redis import *


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and v.endswith('+00:00'):
            try:
                dct[k] = datetime.datetime.fromisoformat(v)
            except:
                pass
    return dct


async def get_cache(keys: Keys):
    current_hour_cache_key = keys.cache_key()
    current_hour_stats = await redis.get(current_hour_cache_key)

    if current_hour_stats:
        return json.loads(current_hour_stats, object_hook=datetime_parser)


async def set_cache(data, keys: Keys):
    def serialize_dates(v):
        return v.isoformat() if isinstance(v, datetime) else v

    await redis.set(
        keys.cache_key(),
        json.dumps(data, default=serialize_dates),
        ex=TWO_MINUTES,
    )

