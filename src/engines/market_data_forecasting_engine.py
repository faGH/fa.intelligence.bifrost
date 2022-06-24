from pandas import DataFrame


class MarketDataForecastingEngine():
    def __init__(self):
        pass

    def get_next_candle_close_prediction(self, market_data: DataFrame) -> float:
        '''Get the predicted next closing price of the asset.'''
        raise NotImplementedError()
