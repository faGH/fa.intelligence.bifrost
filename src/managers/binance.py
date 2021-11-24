from configuration import APP_ROUTE_PREFIX
from models.binance import get_forecast_response
from flask_restx import Namespace, Resource
from datetime import datetime
from flask_restx import reqparse

now = f'{datetime.now()}'.replace(' ', 'T')
api = Namespace(f'{APP_ROUTE_PREFIX}/binance', description='A collection of use-cases for Binance market data.')
forecast_response_model = get_forecast_response(api)

@api.route('pair/<string:pair_name>/period/1h/forecast')
class SpotPairForecast(Resource):
    @api.doc('Spot Pair Forecast', params={
        'pair_name': {'description': 'The pair name that matches that of the Binance exchange for which to forecast. This value is case-insensitive and the underscore is optional.'},
        'cutoff_time': {'in': 'query', 'description': 'The max cutoff time for market data to use. This allows for excluding future data when performing tasks like back-testing.', 'default': f'{now}'},
        'n_forecasts': {'in': 'query', 'description': 'The number of forecasts to make. These forecasts will be the same window size as the period.', 'default': '1'}
    })
    @api.marshal_list_with(forecast_response_model)
    def get(self, pair_name):
        '''Gets X forecasts on a specific pair for the Binance exchange, given a specific cut-off time.'''
        parser = reqparse.RequestParser()
        parser.add_argument('n_forecasts', type=int, default=1)
        parser.add_argument('cutoff_time', type=str, default=now)
        args = parser.parse_args()
        
        cutoff_time = args['cutoff_time']
        n_forecasts = args['n_forecasts']
        
        return { 'response': f'Forecast for pair "{pair_name}" requested. Cutoff: {cutoff_time}. Forecasts: {n_forecasts}.' }, 200