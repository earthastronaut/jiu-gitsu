
class MissingUrlPathParameterError(KeyError):
    """ Parameter missing from url """

    def __init__(self, path, missing_param, **kws):
        self.path = path
        self.missing_param = missing_param
        msg = f"Missing '{missing_param}' from '{path}'"
        super().__init__(msg, **kws)


class DataPipelineError(Exception):
    """ Errors within data pipeline """


class RetryRequest(DataPipelineError):
    """ Request returned error, retry """


class ProgrammingError(DataPipelineError):
    """ For errors caused by misuse of API """
