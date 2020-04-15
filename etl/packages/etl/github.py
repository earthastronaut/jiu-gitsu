import time
import logging

import arrow

import etl
from etl import settings, requests

__all__ = [
    'get_github_auth',
    'create_url_github_repo',
    'GithubCallback',
]


GITHUB_RATELIMIT_REMAINING_BUFFER = 60  # seconds

logger = logging.getLogger(__name__)


class GithubTokenAuth:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'token {self.token[:4]}...'

    def __call__(self, request):
        request.headers["Authorization"] = f'token {self.token}'
        return request


def get_github_auth():
    return GithubTokenAuth(settings.GITHUB_TOKEN)


def fetch_github_ratelimit():
    url = etl.create_url(
        settings.GITHUB_API_BASE_URL,
        'rate_limit/'
    )
    resp = requests.request('get', url)
    data = resp.json()
    rate = data['resources']['core']
    # {
    #     'limit': -1,
    #     'remaining': -1,
    #     'reset': 1586998345,
    # }
    rate['reset_at'] = arrow.Arrow.fromtimestamp(rate['reset'])
    return rate


def display_wait(end, display_interval=60 * 5):
    start = arrow.utcnow()
    now = start
    fmt_wait = str(end - start)
    while now < end:
        fmt_remaining = str(end - now)
        logger.info(f'Waiting... {fmt_remaining} remaining of {fmt_wait}')
        time.sleep(display_interval)
        now = arrow.utcnow()


def github_ratelimit_check():
    rate = fetch_github_ratelimit()
    remaining = rate['remaining']
    logging.info(f'ratelimit remaining {remaining}')
    if remaining < settings.GITHUB_RATELIMIT_REMAINING_MIN:
        logger.info('Waiting...')
        reset_utc_timestamp = rate['reset'] + GITHUB_RATELIMIT_REMAINING_BUFFER
        display_wait(end=arrow.Arrow.fromtimestamp(reset_utc_timestamp))


class GithubCallback:

    def __init__(self, store_data_callback, **store_data_kws):
        self.store_data_callback = store_data_callback
        self.store_data_kws = store_data_kws
        self.retry_backoff = etl.RetryBackoff()

    def __call__(self, response, page_request_kws):
        if response.status_code == 500:
            logger.info(f'Retry... {self.retry_backoff}')
            self.retry_backoff = self.retry_backoff.wait()
            return page_request_kws
        elif response.status_code != 200:
            raise requests.requests.exceptions.RequestException(
                f'invalid status code {response.status_code}'
            )
        data = response.json()
        if len(data) == 0:
            # last page reached, stop paginating
            return
        else:
            self.store_data_callback(data, **self.store_data_kws)

            github_ratelimit_check()

            next_page_request_kws = page_request_kws.copy()
            next_page_request_kws['params']['page'] += 1
            return next_page_request_kws


def create_url_github_repo(*path, **path_params):
    return etl.create_url(
        settings.GITHUB_API_BASE_URL,
        '/repos/{repo_organization_name}/{repo_name}',
        *path, **path_params
    )
