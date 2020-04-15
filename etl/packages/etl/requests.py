import os
import urllib
import time
import random
from collections import namedtuple

import requests

from etl import errors

__all__ = [
    'create_url',
    'request_paginated',
    'request',
    'RetryBackoff',
]

request = requests.request


class RetryBackoff(
    namedtuple(
        'RetryBackoff',
        ['retry', 'retry_limit'],
        defaults=(0, 10),
    )
):
    """ This named tuple contains the retry and retry_limit

    Also a function to implement exponential backoff for an api
    """

    def wait(self):
        if self.retry > self.retry_limit:
            raise requests.exception.RetryError(
                f'Reached retry limit {self.retry_limit}'
            )

        time.sleep(
            (2 ** self.retry) + (random.randint(0, 1000) / 1000)
        )
        return self.__class__(
            retry=self.retry + 1,
            retry_limit=self.retry_limit,
        )


def create_url(netloc, *path, scheme='https', **path_params):
    path_fmt = os.path.join(*path)
    try:
        path_str = path_fmt.format(**path_params).strip('/')
    except KeyError as error:
        missing_param, *_ = error.args
        raise errors.MissingUrlPathParameterError(path_fmt, missing_param)

    return urllib.parse.ParseResult(
        scheme=scheme,
        netloc=netloc,
        path=path_str,
        params='',
        query='',
        fragment='',
    ).geturl()


def _recursive_paginated_request(
        page_request_kws,
        callback=None,
        page_limit=None,
        max_page_limit=1000,
        # recursive arguments:
        page=1
):
    """ See paginated_request
    """
    response = requests.request(**page_request_kws)

    if callback is None:
        return response

    next_page_request_kws = callback(response, page_request_kws)

    if next_page_request_kws is None:
        return

    elif isinstance(next_page_request_kws, dict):
        page += 1

        if page > max_page_limit:
            raise requests.exceptions.RequestException(
                f'reached max page limit {max_page_limit}'
            )
        elif page_limit is not None:
            if page >= page_limit:
                return

        return _recursive_paginated_request(
            page_request_kws,
            callback=callback,
            page_limit=page_limit,
            max_page_limit=max_page_limit,
            # recursive arguments:
            page=page,
        )

    else:
        raise TypeError(
            f'callback "{callback}" returned invalid object {type(next_page_request_kws)}'  # noqa
        )


def request_paginated(
        method, url,
        callback='request',
        page_limit=None,
        max_page_limit=1000,
        **request_kws):
    """ Call requests.request and paginate through

    Parameters:
        method (str): method for the new :class:`Request` object.
        url (str): URL for the new :class:`Request` object.
        callback (callable, str): Receives the response and processes it and
            returns the parameters for the next request. If no parameters are
            returned then stops paginating.
            ```
            next_page_kws = callback(response, page_request_kws)

            ```
        page_limit (int): Stop limit for number of pages.
        max_page_limit (int): Upper limit to the number of pages which can be
            returned. Prevents from inf loops for programming errors.
        **request_kws: passed to `requests.request(method, url, **request_kws)`

    Returns:
        None
    """
    if page_limit is not None and page_limit > max_page_limit:
        raise ValueError(
            f'max_page_limit ({max_page_limit}) < ({page_limit}) page_limit'
        )

    request_kws['method'] = method
    request_kws['url'] = url

    _recursive_paginated_request(
        request_kws,
        callback=callback,
        page_limit=page_limit,
        max_page_limit=max_page_limit,
    )
