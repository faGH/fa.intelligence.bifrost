# For different field types, see https://flask-restx.readthedocs.io/en/latest/_modules/flask_restx/fields.html. Float is everything we need for now.
from datetime import datetime
from flask_restx import fields


def get_next_response(api):
    next_model = api.model('Next', {
        'pair_name': fields.String(description='The pair name of next value.'),
        'predicted_close': fields.Float(description='The predicted closing price of the asset for the next candle.')
    })

    return next_model


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
    def __init__(self, pair_name: str, period: str, cutoff_time_utc: datetime):
        self.pair_name = pair_name.replace('_', '').replace('-', '').replace('/', '').upper()
        self.period = period
        self.cutoff_time_utc = cutoff_time_utc


class Forecast:
    def __init__(self, timestamp_utc: datetime, close: float):
        self.timestamp_utc = timestamp_utc
        self.close = close


class ForecastResponse:
    def __init__(self, pair_name: str, forecasts: list):
        self.pair_name = pair_name.replace('_', '').upper()
        self.forecasts = forecasts


class NextReponse:
    def __init__(self, pair_name: str, predicted_close: float):
        self.pair_name = pair_name.replace('_', '').upper()
        self.predicted_close = predicted_close
