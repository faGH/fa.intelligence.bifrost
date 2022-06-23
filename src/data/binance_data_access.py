from models.binance import ForecastRequest
from pandas import DataFrame
from .config_data_access import ConfigDataAccess
import requests
import json
import pandas as pd
from datetime import datetime as dt, timedelta
import os


class BinanceDataAccess():
    def __init__(self, config_data_access: ConfigDataAccess):
        if config_data_access is None:
            raise Exception('Valid config_data_access is required.')

        self.base_url = config_data_access.binance_base_api_url
        self.data_dir_path = f'{os.getcwd()}/{config_data_access.data_dir_relative_path}'

    def __get_market_data_from_binance__(self, pair: str, start_time_ms, end_time_ms, period: str):
        url = f'{self.base_url}/klines'
        request = {
            'symbol': pair,
            'interval': period,
            'startTime': start_time_ms,
            'endTime': end_time_ms
        }
        response = requests.get(url, params=request)
        response_text = response.text

        if not response.status_code == 200:
            raise Exception(f'Failed to fetch market data from Binance with error: {response_text}')

        return json.loads(response_text)

    def __get_market_data_from_cache__(self, pair: str, period: str):
        fs_path = f'{self.data_dir_path}/{pair}/{period}.txt'
        response = []

        if os.path.exists(fs_path):
            print(f'Reading from cache path "{fs_path}".')

            with open(fs_path, 'r') as f:
                response = json.loads(f.read())
        else:
            print(f'Creating path "{fs_path}".')

            if not os.path.exists(self.data_dir_path):
                os.mkdir(self.data_dir_path)
            if not os.path.exists(f'{self.data_dir_path}/{pair}'):
                os.mkdir(f'{self.data_dir_path}/{pair}')
            if not os.path.exists(fs_path):
                with open(fs_path, 'w') as f:
                    f.write(json.dumps(response))

        return response

    def __json_to_market_data_frame__(self, json_data):
        data = pd.DataFrame(json_data)
        data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
        data.index = [dt.fromtimestamp(x / 1000.0) for x in data.datetime]
        data = data.astype(float)

        return data

    def __cache_market_data__(self, pair: str, period: str, data):
        fs_path = f'{self.data_dir_path}/{pair}/{period}.txt'

        with open(fs_path, 'w') as f:
            f.write(json.dumps(data))

    def get_market_data(self, request: ForecastRequest) -> DataFrame:
        '''Get the kline market data for a given symbol <pair> with a candle length of <period>, for <window_length_in_days> days ago to now.'''
        now = dt.now()
        pair = request.pair_name
        start = str(int((dt(now.year, now.month, now.day) - timedelta(days=self.window_length_in_days)).timestamp() * 1000))
        end = str(int(now.timestamp() * 1000))

        print(f'Fetching data for "{pair}" from "{start}" to "{end}" ({self.window_length_in_days} days).')

        data = self.__get_market_data_from_cache__(pair, request.period)
        last_cache_entry = int(start)

        if len(data) > 1:
            last_cache_entry = data[-1][0]

        last_cache_entry_time = str(last_cache_entry)
        last_cache_entry_datetime = dt.fromtimestamp(last_cache_entry / 1000)

        while not (last_cache_entry_datetime.day == now.day and last_cache_entry_datetime.month == now.month and last_cache_entry_datetime.year == now.year and last_cache_entry_datetime.hour == now.hour):
            delta_data = self.__get_market_data_from_binance__(pair, last_cache_entry_time, end, request.period)
            data = data + delta_data

            if len(data) <= 1:
                return None

            last_cache_entry = data[-1][0]
            last_cache_entry_time = str(last_cache_entry)
            last_cache_entry_datetime = dt.fromtimestamp(last_cache_entry / 1000)
            self.__cache_market_data__(pair, request.period, data)

        return self.__json_to_market_data_frame__(data)
