from expiringdict import ExpiringDict
import logging


class MemoryCacheDataAccess():
    def __init__(self, cache_max_age_in_seconds: int = 10, max_allowed_items=2147483647):
        '''Initialize the cache store with a max time in seconds each entry is allowed to live for as well as a max item count before killing off older entries, defaulted to INT.MAX_VALUE.'''
        self.__cache__ = ExpiringDict(max_len=max_allowed_items,
                                      max_age_seconds=cache_max_age_in_seconds)

    def get_from_cache(self, key: str):
        '''Fetch data from cache should the key exist. Otherwise None.'''
        if key is None:
            raise Exception('Valid key is required.')

        value = self.__cache__.get(key)

        if value is None:
            logging.warning(f'No item with the key "{key}" existed in the cache.')
        else:
            logging.info(f'Item for key "{key}" retrieved from cache with value: {value}')

        return value

    def write_to_cache(self, key: str, data):
        '''Write data to the cache for a given key.'''
        if key is None:
            raise Exception('Valid key is required.')

        if data is None:
            raise Exception('Valid data is required.')

        logging.info(f'Setting cache key "{key}" with value: {data}')

        self.__cache__[key] = data
