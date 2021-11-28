# For different field types, see https://flask-restx.readthedocs.io/en/latest/_modules/flask_restx/fields.html. Float is everything we need for now.
from datetime import datetime
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

class ForecastRequest:
    def __init__(self, pair_name: str, period: str, cutoff_time_utc: datetime, n_forecasts: int):
        self.pair_name = pair_name.replace('_', '').upper()
        self.period = period
        self.cutoff_time_utc = cutoff_time_utc
        self.n_forecasts = n_forecasts

class Forecast:
    def __init__(self, timestamp_utc: datetime, close: float):
        self.timestamp_utc = timestamp_utc
        self.close = close

class ForecastResponse:
    def __init__(self, pair_name: str, forecasts: list):
        self.pair_name = pair_name.replace('_', '').upper()
        self.forecasts = forecasts