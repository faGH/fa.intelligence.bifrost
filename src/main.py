from configuration import HOST_IP_RANGE, HOST_PORT, APP_NAME, APP_DESCRIPTION, APP_VERSION
import flask
from flask_restx import Api

# Bootstrap the application skeleton.
app = flask.Flask(__name__)
api = Api(
    app, 
    version=APP_VERSION, 
    title=f'{APP_NAME} API',
    description=APP_DESCRIPTION
)

# Register modules.
import managers.binance

# Run the web host.
app.run(host=HOST_IP_RANGE, port=HOST_PORT)