import os 
import importlib
import logging
import logging.config

settings_module_name = os.environ.get('SETTINGS_MODULE', None)
if settings_module_name is None:
    try:
        settings_module_name = 'local_settings'
        settings = importlib.import_module(settings_module_name)
    except ImportError:
        settings_module_name = 'gitsu.conf.base'
        settings = importlib.import_module(settings_module_name)
else:
    settings = importlib.import_module(settings_module_name)        


if settings.CONFIGURE_LOGGING:
    if isinstance(settings.LOGGING_CONFIG, str):
        logging.basicConfig(filename=settings.LOGGING_CONFIG)
    else:
        logging.config.dictConfig(settings.LOGGING_CONFIG)
        
    if settings.LOGGING_LEVEL is not None:
        logging.root.setLevel(settings.LOGGING_LEVEL)
