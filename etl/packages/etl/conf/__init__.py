import os
import logging
import logging.config
import importlib


CONFIG_MODULE = os.environ['APP_CONFIG']

settings = importlib.import_module(CONFIG_MODULE)

logging.config.dictConfig(settings.LOGGING)
