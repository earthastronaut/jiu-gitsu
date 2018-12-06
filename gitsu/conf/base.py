""" Global settings for the app

The settings module is imported in the conf.py module and can be accessed from there. 
Look to the conf.py module to find the environment variable use to specify arbirary
settings modules.

"""
import os 
import logging

# =========================================================================== #
# logging

CONFIGURE_LOGGING = True # if False, logger will not be configured
LOGGING_LEVEL = None  # debug, info, warning, error/exception, critical
LOGGING_CONFIG = {  # used in logging.config.dictConfig(...)
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': (
                '{asctime} {process} {module:10}:L{lineno} {levelname:8}'
                ' | {message}'
            ),
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': { 
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }, 
    },
    'root': {
        'handlers': ['console'],
        'level': logging.DEBUG,
    },  
    'loggers': {
        'github3.py': {
            'handlers': ['console'],
            'level': logging.DEBUG,
        }

    }  
}

# =========================================================================== #
# System Paths

MODULE_ROOT_PATH = os.path.dirname(
    os.path.dirname(__file__)
)

PROJECT_PATH = os.path.dirname(
    MODULE_ROOT_PATH
)


DATA_PATH = os.path.join(
    PROJECT_PATH, 'data'
)


# =========================================================================== #
# Application settings 
DEBUG = False

# =========================================================================== #

DB_CONNECTION_PATTERN = (
    '{engine}://{username}:{password}@{host}:{port}/{database}'
)

DATABASES = {
    'db_example_name': {
        'engine': 'postgresql+psycopg2',
        'username': '',
        'password': '',
        'host': '10.0.0.0',
        'port': 5432,
        'database': '',
    },
}

