from configuration import APP_ROUTE_PREFIX
from data.binance_data_access import BinanceDataAccess
from data.fs_cache_data_access import FsCacheDataAccess
from engines.bifrost_gradient_booster_engine import BifrostGradientBoosterEngine
from engines.market_data_forecasting_engine import MarketDataForecastingEngine
from models.binance import NextReponse, BulkRequest, BulkReponse, get_next_response, get_bulk_response, ForecastRequest
from flask_restx import Namespace, Resource
from datetime import datetime
from dateutil import parser as date_parser
from flask_restx import reqparse
from data.config_data_access import ConfigDataAccess
import pandas as pd
import numpy as np

config_data_access = ConfigDataAccess()
cache_data_access = FsCacheDataAccess(config_data_access)
data_access = BinanceDataAccess(config_data_access, cache_data_access=cache_data_access)
market_data_forecasting_engine = MarketDataForecastingEngine()
now = f'{datetime.utcnow()}'.replace(' ', 'T')
api = Namespace(f'{APP_ROUTE_PREFIX}/binance', description='A collection of use-cases for Binance market data.')
next_response_model = get_next_response(api)
bulk_response_model = get_bulk_response(api)


@api.route('/pair/<string:pair_name>/period/<string:period>/next')
class BinanceNextPredictionManager(Resource):
    @api.doc('Spot Pair Forecast', params={
        'pair_name': {'description': 'The pair name that matches that of the Binance exchange for which to forecast. This value is case-insensitive and the underscore is optional.', 'default': 'DOGEBTC'},
        'period': {'description': 'The window period for the candlestick lengths. Currently only 1h is supported.', 'default': '1h'},
        'cutoff_time_utc': {'in': 'query', 'description': 'The max cutoff time for market data to use. This allows for excluding future data when performing tasks like back-testing.', 'default': f'{now}'}
    })
    @api.marshal_with(next_response_model)
    def get(self, pair_name: str, period: str) -> NextReponse:
        '''Gets the next candle price on a specific pair for the Binance exchange, given a specific cut-off time.'''
        request: ForecastRequest = self.__get_parsed_request(pair_name, period)
        market_data: pd.DataFrame = data_access.get_market_data(request)
        cutoff_date: str = f'{request.cutoff_time_utc.year}-{request.cutoff_time_utc.month}-{request.cutoff_time_utc.day}'
        market_data.index = market_data.time
        market_data = market_data.loc[:cutoff_date]
        prior_candle_close, prior_candle_time, predicted_close, predicted_candle_time = market_data_forecasting_engine.get_next_candle_close_prediction(market_data, period)
        delta_percentage: float = self.__calculate_percentage_difference__(prior_candle_close, predicted_close)
        response = NextReponse(pair_name=pair_name,
                               prior_candle_close=prior_candle_close,
                               prior_candle_time=prior_candle_time,
                               predicted_close=predicted_close,
                               predicted_candle_time=predicted_candle_time,
                               delta_percentage=delta_percentage)

        return response, 200

    def __calculate_percentage_difference__(self, x: float, y: float) -> float:
        return (x - y) / ((x + y) / 2)

    def __get_parsed_request(self, pair_name: str, period: str) -> ForecastRequest:
        parser = reqparse.RequestParser()
        parser.add_argument('cutoff_time_utc', type=str, default=now)
        args = parser.parse_args()

        cutoff_time_utc = args['cutoff_time_utc']

        return ForecastRequest(pair_name, period, date_parser.parse(cutoff_time_utc))


@api.route('/pair/<string:pair_name>/period/<string:period>/bulk/<int:count_including_latest>')
class BinanceBulkPredictionManager(Resource):
    @api.doc('Spot Pair Bulk Forecast', params={
        'pair_name': {'description': 'The pair name that matches that of the Binance exchange for which to forecast. This value is case-insensitive and the underscore is optional.', 'default': 'DOGEBTC'},
        'period': {'description': 'The window period for the candlestick lengths. Currently only 1h is supported.', 'default': '1h'},
        'count_including_latest': {'description': 'The count of days to make predictions from and up to the latest candle inclusively.', 'default': '45'}
    })
    @api.marshal_with(bulk_response_model)
    def get(self, pair_name: str, period: str, count_including_latest: int) -> BulkReponse:
        '''Gets the next candle prices for the last X records from the latest candle inclusively.'''
        request = self.__get_parsed_request(pair_name, period, count_including_latest)
        market_data: pd.DataFrame = data_access.get_market_data(request)
        prior_candle_time_delta: np.timedelta64 = np.timedelta64(count_including_latest, 'D')
        date_filter_criteria: str = str(market_data.time.values[-1] - prior_candle_time_delta)
        filtered_market_data: pd.DataFrame = market_data.loc[date_filter_criteria:]
        times: list = []
        actual_closing_prices: list() = []
        predicted_closing_prices: list = []
        detla_percentages: list = []
        trained_model: BifrostGradientBoosterEngine = market_data_forecasting_engine.get_trained_model(market_data, period)

        for index, row in filtered_market_data.iterrows():
            time = row['time']
            actual_close = row['close']
            cutoff_date = str(time)
            market_data = market_data.loc[:cutoff_date]
            predicted_close = trained_model.predict(future_data=filtered_market_data.loc[str(index):].head(1)).values[0]
            times.append(cutoff_date)
            actual_closing_prices.append(actual_close)
            predicted_closing_prices.append(predicted_close)
            detla_percentages.append(self.__calculate_percentage_difference__(actual_close, predicted_close))

        response: BulkReponse = BulkReponse(pair_name, times, actual_closing_prices, predicted_closing_prices, detla_percentages)

        return response, 200

    def __calculate_percentage_difference__(self, x: float, y: float) -> float:
        return (y - x) / ((x + y) / 2)

    def __get_parsed_request(self, pair_name: str, period: str, count_including_latest: int) -> BulkReponse:
        return BulkRequest(pair_name, period, count_including_latest)
