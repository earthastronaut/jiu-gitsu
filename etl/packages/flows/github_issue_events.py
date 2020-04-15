# 1. download_github_issue_events.py
# 1. etl_github_users.py
# 1. etl_github_issue_events.py
import os

from prefect import task, Flow

from tasks import (
    download_github_issue_events,
    etl_github_users,
    etl_github_issue_events,
)


def build_flow():
    name = os.path.basename(__file__).strip('.py')
    kws = dict(
        log_stdout=True,
    )
    with Flow(name) as flow:

        t = task(download_github_issue_events.main, name='download_github_issue_events', **kws)()  # noqa
        t |= task(etl_github_users.main, name='etl_github_users', **kws)()  # noqa
        t |= task(etl_github_issue_events.main, name='etl_github_issue_events', **kws)()  # noqa

    # TODO: flow.schedule =
    return flow


flow = build_flow()

if __name__ == '__main__':
    from prefect.utilities.debug import raise_on_exception
    with raise_on_exception():
        flow.run()
