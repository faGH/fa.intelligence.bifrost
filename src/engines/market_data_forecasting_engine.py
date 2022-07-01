from pandas import DataFrame
import pandas as pd
import numpy as np
import re
from .bifrost_gradient_booster_engine import BifrostGradientBoosterEngine


class MarketDataForecastingEngine():
    '''A class that performs forecasts for given market data.'''
    def __init__(self):
        pass

    def get_trained_model(self, market_data: DataFrame, period: str) -> BifrostGradientBoosterEngine:
        '''Create and train the model.'''
        return BifrostGradientBoosterEngine(data=market_data.copy(),
                                            column_name_to_predict='close',
                                            data_time_column_name='time',
                                            enable_global_scaling=True) \
            .fit(enable_hyperparameter_optimization=False)

    def get_next_candle_close_prediction(self, market_data: DataFrame, period: str) -> float:
        '''Get the predicted next closing price of the asset.'''
        predictions: pd.Series = self.get_trained_model(market_data, period) \
            .predict(future_data=market_data.iloc[-1:])
        prediction_candle_close: float = predictions.values[0]
        prior_candle_close: float = market_data.close.values[-1]
        prior_candle_time: np.datetime64 = market_data.time.values[-1]
        period_split: list = re.split('(\\d+)', period)
        prior_candle_time_delta: np.timedelta64 = np.timedelta64(int(period_split[1]), period_split[2])

        return (prior_candle_close, prior_candle_time, prediction_candle_close, (prior_candle_time + prior_candle_time_delta))
