import datetime
import time
import logging

import github3

from etl.conf import settings

GITHUB_RATELIMIT_REMAINING_MIN = 10
GITHUB_RATELIMIT_WAIT_TIME = 15.0 * 60.0


logger = logging.getLogger(__name__)


def create_github_client():
    """ Creates a client with new baked in session """
    github_client = (
        github3
        .login(
            token=settings.GITHUB_TOKEN,
        )
    )
    return github_client


def display_wait(wait, display_interval=60):
    start = time.time()
    end = start + wait
    now = start
    fmt_wait = str(datetime.timedelta(seconds=wait))
    while now < end:
        fmt_remaining = str(datetime.timedelta(seconds=(end - now)))
        logger.info(f'Waiting... {fmt_remaining} remaining of {fmt_wait}')
        time.sleep(display_interval)
        now = time.time()


def execute_github_iterator(iterator, page_callback):
    prev_req_url = None
    items = []
    for item in iterator:
        # if the page changed, log progress information
        req_url = iterator.last_response.url
        if req_url != prev_req_url:
            page_callback(items)
            items = []
            prev_req_url = req_url
            remaining = iterator.ratelimit_remaining
            logging.info(f'ratelimit remaining {remaining}')
            if remaining < GITHUB_RATELIMIT_REMAINING_MIN:
                logger.info('Waiting...')
                display_wait(GITHUB_RATELIMIT_WAIT_TIME)
        else:
            items.append(item)
    if len(items):
        page_callback(items)
