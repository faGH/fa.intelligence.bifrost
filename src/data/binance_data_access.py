from models.binance import ForecastRequest
from pandas import DataFrame
from .config_data_access import ConfigDataAccess
from .fs_cache_data_access import FsCacheDataAccess
import requests
import json
import pandas as pd
from datetime import datetime as dt, timedelta
import numpy as np


class BinanceDataAccess():
    '''A client for fetching market information from the Binance exchange.'''
    def __init__(self, config_data_access: ConfigDataAccess, cache_data_access: FsCacheDataAccess):
        if config_data_access is None:
            raise Exception('Valid config_data_access is required.')

        if cache_data_access is None:
            raise Exception('Valid cache_data_access is required.')

        self.base_url = config_data_access.binance_base_api_url
        self.cache_data_access = cache_data_access
        self.window_length_in_days = config_data_access.window_length_in_days

    def __get_market_data_from_binance__(self, pair: str, start_time_ms: int, end_time_ms: int, period: str) -> list:
        '''Fetch symbol price information from Binance'''
        url: str = f'{self.base_url}/klines'
        request: dict = {
            'symbol': pair,
            'interval': period,
            'startTime': start_time_ms,
            'endTime': end_time_ms
        }
        response: requests.Response = requests.get(url, params=request)
        response_text: str = response.text

        if not response.status_code == 200:
            raise Exception(f'Failed to fetch market data from Binance with error: {response_text}')

        return json.loads(response_text)

    def __get_market_data_from_cache__(self, pair: str, period: str) -> list:
        '''Get pair market data from cache first.'''
        key: str = f'{pair}.{period}'
        response: list = self.cache_data_access.get_from_cache(key=key)

        if response is None:
            return []

        return response

    def __json_to_market_data_frame__(self, json_data: list) -> pd.DataFrame:
        '''Convert the market data json into a dataframe.'''
        data: pd.DataFrame = pd.DataFrame(json_data)
        data.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
        data = data.iloc[:, :6]
        data['time'] = pd.to_datetime(data['time'], unit='ms')
        data['open'] = data['open'].astype(np.float64)
        data['high'] = data['high'].astype(np.float64)
        data['low'] = data['low'].astype(np.float64)
        data['close'] = data['close'].astype(np.float64)
        data['volume'] = data['volume'].astype(np.float64).astype(np.int64)
        data.index = data['time']

        return data

    def __cache_market_data__(self, pair: str, period: str, data):
        '''Persist pair market data to cache.'''
        key: str = f'{pair}.{period}'

        self.cache_data_access.write_to_cache(key=key, data=data)

    def get_market_data(self, request: ForecastRequest) -> DataFrame:
        '''Get the kline market data for a given symbol <pair> with a candle length of <period>, for <window_length_in_days> days ago to now.'''
        now: int = dt.now()
        pair: str = request.pair_name
        start: str = str(int((dt(now.year, now.month, now.day) - timedelta(days=self.window_length_in_days)).timestamp() * 1000))
        end: str = str(int(now.timestamp() * 1000))

        print(f'Fetching data for "{pair}" from "{start}" to "{end}" ({self.window_length_in_days} days).')

        data: list = self.__get_market_data_from_cache__(pair, request.period)
        last_cache_entry: int = int(start)

        if len(data) > 1:
            last_cache_entry = data[-1][0]

        last_cache_entry_time: str = str(last_cache_entry)
        last_cache_entry_datetime: dt = dt.fromtimestamp(last_cache_entry / 1000)
        last_delta_data: list = None

        while not (last_cache_entry_datetime.day == now.day and last_cache_entry_datetime.month == now.month and last_cache_entry_datetime.year == now.year and last_cache_entry_datetime.hour == now.hour):
            delta_data: list = self.__get_market_data_from_binance__(pair, last_cache_entry_time, end, request.period)

            if last_delta_data == delta_data:
                break

            data: list = data + delta_data

            if len(data) <= 1:
                return None

            last_cache_entry = data[-1][0]
            last_cache_entry_time = str(last_cache_entry)
            last_cache_entry_datetime = dt.fromtimestamp(last_cache_entry / 1000)
            self.__cache_market_data__(pair, request.period, data)
            last_delta_data = delta_data

        return self.__json_to_market_data_frame__(data)
