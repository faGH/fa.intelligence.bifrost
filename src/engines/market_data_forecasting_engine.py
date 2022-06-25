from pandas import DataFrame
from .bifrost_gradient_booster_engine import BifrostGradientBoosterEngine


class MarketDataForecastingEngine():
    def __init__(self):
        pass

    def get_next_candle_close_prediction(self, market_data: DataFrame) -> float:
        '''Get the predicted next closing price of the asset.'''
        predictions = BifrostGradientBoosterEngine(data=market_data.copy(),
                                                   column_name_to_predict='close',
                                                   data_time_column_name='time',
                                                   enable_global_scaling=True) \
            .fit(enable_hyperparameter_optimization=False) \
            .predict(future_data=market_data.iloc[-1:])

        return predictions.values[0]
