#!env python
import logging
import github3
import time
import pytz
import dateutil.parser

import etl


logger = logging.getLogger(__name__)


class GithubIssuesCallback:

    def __init__(self, repo, organization):
        self.repo = repo
        self.organization = organization
        self.created = []

    def callback(self, issue):
        if isinstance(issue, dict):
            data = issue
        else:
            data = issue._json_data

        data['repo'] = {
            'name': self.repo,
            'organization_name': self.organization,
        }

        key = 'github_issue_{}'.format(data['id'])
        with etl.db_session_context() as sess:
            obj = None
            created = (
                not
                etl
                .models
                .DataLake
                ._query
                .exists(_session=sess, key=key)
            )
            if created:
                obj = etl.models.DataLake(
                    key=key, schema='github_issue', data=data,
                )
                sess.add(obj)
        self.created.append(created)
        return created

    def new_page_callback(self, iterator, item):
        ratelimit_remaining = getattr(iterator, 'ratelimit_remaining', -1)
        if ratelimit_remaining < 10:
            logger.info('Waiting...')
            time.sleep(15.0 * 60.0)

        n = len(self.created)
        s = sum(self.created)
        if n > 1 and s == 0:
            raise Exception('stop!')
        self.created = []
        etl.github.github_default_new_page_callback(iterator, item)


def download_github_issues_for_repo(repo, organization, since=None):
    if since is None:
        raise NotImplementedError('Infer from data, the max issue updated')
    elif isinstance(since, str):
        since = (
            dateutil
            .parser
            .parse(since)
            .replace(tzinfo=pytz.UTC)
            .isoformat()
        )

    # Get the Github repo object
    repo = (
        github3
        .login(
            token=etl.settings.GITHUB_TOKEN,
        )
        .repository(organization, repo)
    )

    # create an issues iterator to access all the issues
    iter_issues = repo.issues(
        # YYYY-MM-DDTHH:MM:SSZ
        # since='2018-05-01T00:00:00Z',
        since=since,
        sort='updated',
        direction='asc',
        state='all',
    )
    iter_issues.params.update({
        'page': 1,
        'per_page': 300,
    })

    c = GithubIssuesCallback(
        repo=repo,
        organization=organization,
    )

    issues = etl.github.github_iterator_results(
        iter_issues,
        callback=c.callback,
        new_page_callback=c.new_page_callback,
    )
    return issues


def main(organization_repo=None, since=None, **context):
    if organization_repo is not None:
        organization, repo = organization_repo.split('/')
    else:
        # TODO: get watched repos
        organization = 'WordPress'
        repo = 'gutenberg'

    # TODO: SINCE==none should infer from the data
    # TODO: Since should be passed in with airflow?
    if since is None:
        since = '2000-01-01T00:00'

    download_github_issues_for_repo(repo, organization, since=since)


if __name__ == '__main__':
    main(
        since='2019-11-01T00:00'
    )
