from configuration import APP_ROUTE_PREFIX
from data.binance_data_access import BinanceDataAccess
from engines.market_data_forecasting_engine import MarketDataForecastingEngine
from models.binance import ForecastResponse, get_forecast_response, ForecastRequest
from flask_restx import Namespace, Resource
from datetime import datetime
from dateutil import parser as date_parser
from flask_restx import reqparse
from data.config_data_access import ConfigDataAccess

config_data_access = ConfigDataAccess()
data_access = BinanceDataAccess(config_data_access)
market_data_forecasting_engine = MarketDataForecastingEngine()
now = f'{datetime.utcnow()}'.replace(' ', 'T')
api = Namespace(f'{APP_ROUTE_PREFIX}/binance', description='A collection of use-cases for Binance market data.')
forecast_response_model = get_forecast_response(api)

@api.route('/pair/<string:pair_name>/period/<string:period>/forecast')
class SpotPairForecast(Resource):
    @api.doc('Spot Pair Forecast', params={
        'pair_name': {'description': 'The pair name that matches that of the Binance exchange for which to forecast. This value is case-insensitive and the underscore is optional.', 'default': 'ETHBTC'},
        'period': {'description': 'The window period for the candlestick lengths. Currently only 1h is supported.', 'default': '1h'},
        'cutoff_time_utc': {'in': 'query', 'description': 'The max cutoff time for market data to use. This allows for excluding future data when performing tasks like back-testing.', 'default': f'{now}'},
        'n_forecasts': {'in': 'query', 'description': 'The number of forecasts to make. These forecasts will be the same window size as the period.', 'default': '5'}
    })
    @api.marshal_with(forecast_response_model)
    def get(self, pair_name: str, period: str) -> ForecastResponse:
        '''Gets X forecasts on a specific pair for the Binance exchange, given a specific cut-off time.'''
        request = self.__get_parsed_request(pair_name, period)
        market_data = data_access.get_market_data(request)
        response = market_data_forecasting_engine.get_forecasts(market_data)
        
        return response, 200
    
    def __get_parsed_request(self, pair_name: str, period: str) -> ForecastRequest:
        parser = reqparse.RequestParser()
        parser.add_argument('n_forecasts', type=int, default=5)
        parser.add_argument('cutoff_time_utc', type=str, default=now)
        args = parser.parse_args()
        
        cutoff_time_utc = args['cutoff_time_utc']
        n_forecasts = args['n_forecasts']
        
        return ForecastRequest(pair_name, period, date_parser.parse(cutoff_time_utc), n_forecasts)