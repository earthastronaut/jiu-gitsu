import os

# =========================================================================== #
# Configuration File
# =========================================================================== #

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

# /usr/local/app
APP_PATH = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                __file__
            )
        )
    )
)

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
LOGGING = {
    'version': 1,
    'disable_existing_logging': False,
    'formatters': {
        'default': {
            'format': '{asctime} {process} {module:10}:L{lineno} {levelname:8} | {message}',  # noqa
            'datefmt': '%Y-%m-%dT%H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    },
    'loggers': {
        'ipython': {
            'level': 'CRITICAL',
        },
    }
}


# --------------------------------------------------------------------------- #
# Databases
# --------------------------------------------------------------------------- #

DATABASES = {
    'default': {
        'engine': 'postgresql+psycopg2',
        'username': os.environ['POSTGRES_USER'],
        'database': os.environ['POSTGRES_DB'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'host': os.environ['POSTGRES_HOST'],
        'port': os.environ.get('POSTGRES_PORT', 5432),
    }
}

# --------------------------------------------------------------------------- #
# Project
# --------------------------------------------------------------------------- #

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
