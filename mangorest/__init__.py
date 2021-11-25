__version__ = "0.1.0"


import logging.config

from flask import Flask

from . import config

logging.config.dictConfig(config.LOGGING_CONFIG)

app = Flask(__name__)

import mangorest.views
