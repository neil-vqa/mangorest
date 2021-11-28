__version__ = "0.1.0"


import logging.config

from flask import Flask

from . import config

logging.config.dictConfig(config.LOGGING_CONFIG)

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY

import mangorest.views
