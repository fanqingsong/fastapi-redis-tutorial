from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import FastAPI

from service.cache import *

from service.timeseries import *


app = FastAPI(title='FastAPI Redis Tutorial')


def get_direction(last_three_hours, key: str):
    if last_three_hours[0][key] < last_three_hours[-1][key]:
        return 'rising'
    elif last_three_hours[0][key] > last_three_hours[-1][key]:
        return 'falling'
    else:
        return 'flat'


def now():
    """Wrap call to utcnow, so that we can mock this function in tests."""
    return datetime.utcnow()


async def calculate_three_hours_of_data(keys: Keys) -> Dict[str, str]:
    print("------------------------------------------")
    sentiment_key = keys.timeseries_sentiment_key()
    price_key = keys.timeseries_price_key()

    three_hours_ago_ms = int((now() - timedelta(days=465)).timestamp() * 1000)
    print("---- three_hours_ago_ms ------")
    print(three_hours_ago_ms)

    sentiment = await get_hourly_average(sentiment_key, three_hours_ago_ms)
    price = await get_hourly_average(price_key, three_hours_ago_ms)

    print(price)
    print(sentiment)

    last_three_hours = [
        {
            'price': data[0][1], 
            'sentiment': data[1][1],
            'time': datetime.fromtimestamp(data[0][0] / 1000, tz=timezone.utc),
        }

        for data in zip(price, sentiment)
    ]

    print(last_three_hours)

    return {
        'hourly_average_of_averages': last_three_hours,
        'sentiment_direction': get_direction(last_three_hours, 'sentiment'),
        'price_direction': get_direction(last_three_hours, 'price'),
    }


async def persist(keys: Keys, data: BitcoinSentiments):
    ts_sentiment_key = keys.timeseries_sentiment_key()
    ts_price_key = keys.timeseries_price_key()

    await add_many_to_timeseries(
        (
            (ts_price_key, 'btc_price'),
            (ts_sentiment_key, 'mean'),
        ), data,
    )


@app.post('/refresh')
async def refresh(background_tasks: BackgroundTasks, keys: Keys = Depends(make_keys)):
    async with httpx.AsyncClient(verify=False) as client:
        data = await client.get(SENTIMENT_API_URL)

    # print(data.json())
    # print(keys)

    await persist(keys, data.json())
    
    data = await calculate_three_hours_of_data(keys)
    background_tasks.add_task(set_cache, data, keys)


@app.get('/is-bitcoin-lit')
async def bitcoin(background_tasks: BackgroundTasks, keys: Keys = Depends(make_keys)):
    data = await get_cache(keys)

    if not data:
        data = await calculate_three_hours_of_data(keys)
        background_tasks.add_task(set_cache, data, keys)

    return data



async def initialize_redis(keys: Keys):
    await make_timeseries(keys.timeseries_sentiment_key())
    await make_timeseries(keys.timeseries_price_key())


@app.on_event('startup')
async def startup_event():
    keys = Keys()
    await initialize_redis(keys)
