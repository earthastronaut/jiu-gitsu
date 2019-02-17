import os
import sys
import yaml
import logging
import logging.config
import warnings


CONFIG_PATH = os.environ.get(
    'CONFIG_PATH',
    os.path.dirname(__file__),
)


CONFIG_FILES = os.environ.get(
    'CONFIG_FILES',
    'base.yaml:local_settings.yaml',
)


def _update_relpaths(config, key_suffix='_PATH'):
    """ Updates PATH variables to be relative to server

    Note:
      - MODULE_ROOT_PATH is implied if not overwritten. 
        The implied value is os.path.dirname(__file__)

    Example:

        PROJECT_PATH: '{MODULE_ROOT_PATH}/resources'
        settings.PROJECT_PATH == '/opt/path/module/resources'
    """
    for key, value in config.items():
        if key.endswith(key_suffix):
            relpath = value.format(**config)
            config[key] = os.path.abspath(relpath)


def _resolve_config_filepaths(config_files=None, config_path=None):
    """ Resolves which filepath to load config from

    For each filename in config_files, look in the config_path 
    and locate the first.

    """
    # default config path
    if config_path is None:
        config_path = CONFIG_PATH
    if isinstance(config_path, str):
        config_path = config_path.split(':')

    # default config files
    if config_files is None:
        config_files = CONFIG_FILES
    if isinstance(config_files, str):
        config_files = config_files.split(':')

    config_filepaths = []
    # get filename
    for fn in config_files:
        found = False
        logging.debug('looking for config file "{}"'.format(fn))

        # get path
        for path in config_path:
            logging.debug('looking in path "{}"'.format(path))

            # join into filepath
            fp = os.path.join(path, fn)
            found = os.path.exists(fp)
            if found:
                logging.info('Found config "{}"'.format(fp))
                break
        if found:
            config_filepaths.append(fp)
        else:
            warning = (
                '\nConfig file not found "{}" in {}'
                .format(fn, config_path)
            )
            warnings.warn(warning)
    return config_filepaths


def _load_config(config_filepaths):
    """ Load config files with inheritance

    Load each config file and update the result dictionary.

    """
    # Base Settings
    config = {}
    config['MODULE_ROOT_PATH'] = os.path.dirname(
        os.path.dirname(__file__)
    )

    for fp in config_filepaths:
        with open(fp) as f:
            config.update(yaml.load(f))

    _update_relpaths(config, '_PATH')
    _update_relpaths(config, '_FILEPATH')    
    return config


class Settings:

    def __init__(self, config_files=None, config_path=None):
        kws = dict(
            config_files=config_files, config_path=config_path
        )
        config_filepaths = _resolve_config_filepaths(**kws)
        self.__dict__ = {
            'CONFIG_FILEPATHS': config_filepaths,
        }
        self.__dict__.update(
            _load_config(config_filepaths)
        )
        self._configure_logging()

    def _reload(self, **kws):
        self = Settings(**kws)

    def _configure_logging(self):
        logging_config = getattr(self, 'LOGGING_CONFIG')
        if not logging_config:
            return 
        if isinstance(logging_config, str):
            logging.basicConfig(filename=logging_config)
        else:
            logging.config.dictConfig(logging_config)


# =========================================================================== #
# Load Settings
# =========================================================================== #

settings = Settings()
