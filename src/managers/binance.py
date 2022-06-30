from configuration import APP_ROUTE_PREFIX
from data.binance_data_access import BinanceDataAccess
from data.fs_cache_data_access import FsCacheDataAccess
from engines.market_data_forecasting_engine import MarketDataForecastingEngine
from models.binance import NextReponse, get_next_response, ForecastRequest
from flask_restx import Namespace, Resource
from datetime import datetime
from dateutil import parser as date_parser
from flask_restx import reqparse
from data.config_data_access import ConfigDataAccess
import pandas as pd

config_data_access = ConfigDataAccess()
cache_data_access = FsCacheDataAccess(config_data_access)
data_access = BinanceDataAccess(config_data_access, cache_data_access=cache_data_access)
market_data_forecasting_engine = MarketDataForecastingEngine()
now = f'{datetime.utcnow()}'.replace(' ', 'T')
api = Namespace(f'{APP_ROUTE_PREFIX}/binance', description='A collection of use-cases for Binance market data.')
next_response_model = get_next_response(api)


@api.route('/pair/<string:pair_name>/period/<string:period>/next')
class SpotPairForecast(Resource):
    @api.doc('Spot Pair Forecast', params={
        'pair_name': {'description': 'The pair name that matches that of the Binance exchange for which to forecast. This value is case-insensitive and the underscore is optional.', 'default': 'DOGEBTC'},
        'period': {'description': 'The window period for the candlestick lengths. Currently only 1h is supported.', 'default': '1h'},
        'cutoff_time_utc': {'in': 'query', 'description': 'The max cutoff time for market data to use. This allows for excluding future data when performing tasks like back-testing.', 'default': f'{now}'}
    })
    @api.marshal_with(next_response_model)
    def get(self, pair_name: str, period: str) -> NextReponse:
        '''Gets the next candle price on a specific pair for the Binance exchange, given a specific cut-off time.'''
        request = self.__get_parsed_request(pair_name, period)
        market_data: pd.DataFrame = data_access.get_market_data(request)
        cutoff_date: str = f'{request.cutoff_time_utc.year}-{request.cutoff_time_utc.month}-{request.cutoff_time_utc.day}'
        market_data.index = market_data.time
        market_data = market_data.loc[:cutoff_date]
        prior_candle_close, prior_candle_time, predicted_close, predicted_candle_time = market_data_forecasting_engine.get_next_candle_close_prediction(market_data, period)
        response = NextReponse(pair_name=pair_name,
                               prior_candle_close=prior_candle_close,
                               prior_candle_time=prior_candle_time,
                               predicted_close=predicted_close,
                               predicted_candle_time=predicted_candle_time)

        return response, 200

    def __get_parsed_request(self, pair_name: str, period: str) -> NextReponse:
        parser = reqparse.RequestParser()
        parser.add_argument('cutoff_time_utc', type=str, default=now)
        args = parser.parse_args()

        cutoff_time_utc = args['cutoff_time_utc']

        return ForecastRequest(pair_name, period, date_parser.parse(cutoff_time_utc))
