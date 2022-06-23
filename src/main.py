from configuration import HOST_IP_RANGE, HOST_PORT, APP_NAME, APP_DESCRIPTION, APP_VERSION
import flask
from flask_restx import Api
from managers.binance import api as binance_namespace

# Bootstrap the application skeleton.
app = flask.Flask(__name__)

# Define Swagger API.
api = Api(
    app,
    version=APP_VERSION,
    title=f'{APP_NAME} API',
    description=APP_DESCRIPTION
)

# Register modules.
api.add_namespace(binance_namespace)

# Run the web host.
app.run(host=HOST_IP_RANGE, port=HOST_PORT)
