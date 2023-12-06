from service.keys import *
from utils.log import *

from utils.redis import *
import functools
from aioredis.exceptions import ResponseError


async def add_many_to_timeseries(
    key_pairs: Iterable[Tuple[str, str]],
    data: BitcoinSentiments
):
    """
    Add many samples to a single timeseries key.

    `key_pairs` is an iteratble of tuples containing in the 0th position the
    timestamp key into which to insert entries and the 1th position the name
    of the key within th `data` dict to find the sample.
    """
    partial = functools.partial(redis.execute_command, 'TS.MADD')
    for datapoint in data:
        print(datapoint)

        for timeseries_key, sample_key in key_pairs:
            partial = functools.partial(
                partial, timeseries_key, int(
                    float(datapoint['timestamp']) * 1000,
                ),
                datapoint[sample_key],
            )
    return await partial()


async def get_hourly_average(ts_key: str, top_of_the_hour: int):
    print(ts_key)
    print(top_of_the_hour)

    response = await redis.execute_command(
        'TS.RANGE', ts_key, top_of_the_hour, '+',
        'AGGREGATION', 'avg', HOURLY_BUCKET,
    )

    print(response)

    # Returns a list of the structure [timestamp, average].
    return response


async def make_timeseries(key):
    """
    Create a timeseries with the Redis key `key`.

    We'll use the duplicate policy known as "first," which ignores
    duplicate pairs of timestamp and values if we add them.

    Because of this, we don't worry about handling this logic
    ourselves -- but note that there is a performance cost to writes
    using this policy.
    """
    try:
        await redis.execute_command(
            'TS.CREATE', key,
            'DUPLICATE_POLICY', 'first',
        )
    except ResponseError as e:
        # Time series probably already exists
        log.info('Could not create timeseries %s, error: %s', key, e)

