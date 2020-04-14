# 1. download_github_issues.py
# 1. etl_github_repo.py
# 1. etl_github_users.py
# 1. etl_github_issues.py
import os

from prefect import task, Flow

from tasks import (
    download_github_issues,
    etl_github_repo,
    etl_github_users,
    etl_github_issues,
)

from importlib import reload


def build_flow():
    name = os.path.basename(__file__).strip('.py')
    kws = dict(
        log_stdout=True,
    )
    with Flow(name) as flow:

        t = task(
            download_github_issues.main,
            name='download_github_issues', **kws
        )()
        t |= task(etl_github_repo.main, name='etl_github_repo', **kws)()
        t |= task(etl_github_users.main, name='etl_github_users', **kws)()
        t |= task(etl_github_issues.main, name='etl_github_issues', **kws)()

    # TODO: flow.schedule =

    return flow


flow = build_flow()

if __name__ == '__main__':
    from prefect.utilities.debug import raise_on_exception
    with raise_on_exception():
        flow.run()
