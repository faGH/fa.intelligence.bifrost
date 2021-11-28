from models.binance import ForecastRequest
from pandas import DataFrame

class BinanceDataAccess():
    def __init__(self):
        pass

    def get_market_data(self, request: ForecastRequest) -> DataFrame:
        '''Get the market data for up to the cutoff point in time, using the Binance Data Accessor.'''
        raise Exception('Not Implemented')