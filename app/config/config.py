from utils.common_types import *

DEFAULT_KEY_PREFIX = 'is-bitcoin-lit'
SENTIMENT_API_URL = 'https://api.senticrypt.com/v1/bitcoin.json'
TWO_MINUTES = 60 + 60
HOURLY_BUCKET = '3600000'



class Config(BaseSettings):
    # The default URL expects the app to run using Docker and docker-compose.
    redis_url: str = 'redis://redis:6379'
