from pandas import DataFrame
import pandas as pd
import numpy as np
import re
from .bifrost_gradient_booster_engine import BifrostGradientBoosterEngine
from data.memory_cache_data_access import MemoryCacheDataAccess
from configuration import MODEL_CACHE_IN_SECONDS


class MarketDataForecastingEngine():
    '''A class that performs forecasts for given market data.'''
    def __init__(self):
        self.__model_cache__ = MemoryCacheDataAccess(cache_max_age_in_seconds=MODEL_CACHE_IN_SECONDS)

    def get_trained_model(self, market_data: DataFrame, period: str, asset_name: str) -> BifrostGradientBoosterEngine:
        '''Create and train the model.'''
        model_key: str = f'{asset_name}-{period}'
        model: BifrostGradientBoosterEngine = self.__model_cache__.get_from_cache(model_key)

        if model is not None:
            return model

        model = BifrostGradientBoosterEngine(data=market_data.copy(),
                                             column_name_to_predict='close',
                                             data_time_column_name='time',
                                             enable_global_scaling=True) \
            .fit(enable_hyperparameter_optimization=False)

        self.__model_cache__.write_to_cache(model_key, model)

        return model

    def get_next_candle_close_prediction(self, market_data: DataFrame, period: str, asset_name: str) -> float:
        '''Get the predicted next closing price of the asset.'''
        predictions: pd.Series = self.get_trained_model(market_data, period, asset_name) \
            .predict(future_data=market_data.iloc[-1:])
        prediction_candle_close: float = predictions.values[0]
        prior_candle_close: float = market_data.close.values[-1]
        prior_candle_time: np.datetime64 = market_data.time.values[-1]
        period_split: list = re.split('(\\d+)', period)
        prior_candle_time_delta: np.timedelta64 = np.timedelta64(int(period_split[1]), period_split[2])

        return (prior_candle_close, prior_candle_time, prediction_candle_close, (prior_candle_time + prior_candle_time_delta))
