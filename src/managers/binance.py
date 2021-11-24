from models.binance import get_forecast_response
from main import api
from flask_restx import Resource

flask_namespace = api.namespace('api/v1/binance', description='A collection of use-cases for Binance market data.')
forecast_response = get_forecast_response()

@api.doc()
@flask_namespace.route('forecast')
class binance_manager(Resource):
    '''Perform a forecast on a specific pair for the Binance exchange, given a specific cut-off time.'''
    #@flask_namespace.marshal_with(forecast_response, code=200)
    def get_spot_pair_forecast(self):
        return 'It works!', 200