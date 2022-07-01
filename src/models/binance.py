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


def get_bulk_response(api):
    data_model = api.model('Data', {
        'time': fields.List(fields.String(description='The time slice that the actual price and predicted price is for.')),
        'actual_closing_prices': fields.List(fields.Float(description='The actual closing price for the given time / candle.')),
        'predicted_close': fields.List(fields.Float(description='The predicted closing price for the following time / candle.'))
    })
    bulk_model = api.model('Bulk', {
        'pair_name': fields.String(description='The pair name of next value.'),
        'data': fields.Nested(data_model)
    })

    return bulk_model


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


class BulkRequest:
    def __init__(self, pair_name: str, period: str, count_including_latest: int):
        self.pair_name = pair_name.replace('_', '').replace('-', '').replace('/', '').upper()
        self.period = period
        self.count_including_latest = count_including_latest


class BulkReponse:
    def __init__(self, pair_name: str, times: list, actual_closing_prices: list, predicted_closing_prices: list):
        self.pair_name = pair_name.replace('_', '').upper()
        self.data = {
            'time': times,
            'actual_closing_prices': actual_closing_prices,
            'predicted_close': predicted_closing_prices
        }
