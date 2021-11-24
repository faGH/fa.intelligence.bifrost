# For different field types, see https://flask-restx.readthedocs.io/en/latest/_modules/flask_restx/fields.html. Float is everything we need for now.
from flask_restx import fields

def get_forecast_response(api):
    response_model = api.model('SpotPairForecastResponse', {
        'response': fields.String(description="Forecast response")
    })
    
    return response_model