# For different field types, see https://flask-restx.readthedocs.io/en/latest/_modules/flask_restx/fields.html. Float is everything we need for now.
from datetime import datetime
from flask_restx import fields


def get_next_response(api):
    next_model = api.model('Next', {
        'pair_name': fields.String(description='The pair name of next value.'),
        'prior_candle_close': fields.Float(description='The closing price of the prior/last candle to the prediction.'),
        'prior_candle_time': fields.String(description='The opening time of the prior/last candle to the prediction.'),
        'predicted_close': fields.Float(description='The predicted closing price of the asset for the next candle.'),
        'predicted_candle_time': fields.String(description='The opening time for the candle that the predicted value is for.')
    })

    return next_model


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
    def __init__(self, pair_name: str, prior_candle_close: float, prior_candle_time: str, predicted_close: float, predicted_candle_time: str):
        self.pair_name = pair_name.replace('_', '').upper()
        self.prior_candle_close = prior_candle_close
        self.prior_candle_time = prior_candle_time
        self.predicted_close = predicted_close
        self.predicted_candle_time = predicted_candle_time
