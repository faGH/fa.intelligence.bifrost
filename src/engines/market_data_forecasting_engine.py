import pandas as pd
from pandas import DataFrame
from .bifrost_gradient_booster_engine import BifrostGradientBoosterEngine


class MarketDataForecastingEngine():
    def __init__(self):
        pass

    def __prep_data__(self, market_data: DataFrame) -> DataFrame:
        market_data['time'] = pd.to_datetime(market_data['close_time'], unit='ms')

        return market_data.drop(columns=['datetime', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore', 'close_time'])

    def get_next_candle_close_prediction(self, market_data: DataFrame) -> float:
        '''Get the predicted next closing price of the asset.'''
        data = self.__prep_data__(market_data)
        predictions = BifrostGradientBoosterEngine(data=data,
                                                   column_name_to_predict='close',
                                                   data_time_column_name='time',
                                                   enable_global_scaling=True) \
            .fit(enable_hyperparameter_optimization=True) \
            .predict(future_data=data.iloc[-1:])

        return predictions.values[0]
