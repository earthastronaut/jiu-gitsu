#!env python
import logging
import github3
import time
import pytz
import dateutil.parser

import etl


logger = logging.getLogger(__name__)


class GithubIssuesCallback:

    data_lake_schema = 'github_issue'
    data_lake_key_fmt = 'github_issue_{id}'

    def __init__(self, github_client, repo):
        self.github_client = github_client
        self.repo = repo
        self.created = []

    def callback(self, issue):
        if isinstance(issue, dict):
            data = issue
        else:
            data = issue._json_data

        data['repo'] = {
            'name': self.repo.repo_name,
            'organization_name': self.repo.repo_organization_name,
        }

        key = self.data_lake_key_fmt.format(**data)
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
                    key=key, schema=self.data_lake_schema, data=data,
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


def download_github_issues_for_repo(repo, since=None):
    if since is None:
        since = '2000-01-01T00:00:00Z'
        # TODO: infer since from data
        logger.warning(
            'Using since={since}. Need to infer from data the max issue updated'
        )

    since = (
        dateutil
        .parser
        .parse(since)
        .replace(tzinfo=pytz.UTC)
        .isoformat()
    )

    # Get the Github repo object
    github_client = (
        github3
        .login(
            token=etl.settings.GITHUB_TOKEN,
        )
        .repository(repo.repo_organization_name, repo.repo_name)
    )

    # create an issues iterator to access all the issues
    iter_issues = github_client.issues(
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
        github_client=github_client,
        repo=repo,
    )

    issues = etl.github.github_iterator_results(
        iter_issues,
        callback=c.callback,
        new_page_callback=c.new_page_callback,
    )
    return issues


def get_watched_repositories():
    return list((
        etl
        .models
        .GitHubRepo
        ._query
        .filter()
    ))


def main(repo_name='gutenberg', organization_name='WordPress', since='2000-01-01T00:00'):

    # TODO: SINCE==none should infer from the data
    # TODO: Since should be passed in with airflow?

    repositories = [
        etl.models.GitHubRepo(
            repo_name=repo_name,
            repo_id=repo_name,
            repo_organzation_name=organization_name,
        )
    ]
    return list(map(download_github_issues_for_repo, repositories))


if __name__ == '__main__':
    main(
        since='2019-11-01T00:00'
    )
