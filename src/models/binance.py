# For different field types, see https://flask-restx.readthedocs.io/en/latest/_modules/flask_restx/fields.html. Float is everything we need for now.
from flask_restx import fields

def get_forecast_response(api):
    forecast_model = api.model('Forecast', {
        'timestamp_utc': fields.DateTime(description='The time for which this forecast is applicable.'),
        'close': fields.Float(description='The forecasted closing price of the asset.')
    })
    response_model = api.model('SpotPairForecastResponse', {
        'pairName': fields.String(description='The pair name used on Binance to fetch market data.'),
        'forecasts': fields.List(fields.Nested(forecast_model))
    })
    
    return response_model