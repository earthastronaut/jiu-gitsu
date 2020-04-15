#!/usr/local/bin/python
import logging

import arrow

import etl
from tasks import constants


logger = logging.getLogger(__name__)


class GithubIssuesCallback:

    def __init__(self, repo):
        self.repo = repo

    def __call__(self, github_issues):
        repo = self.repo

        issues = {}
        for issue in github_issues:
            data = issue._json_data
            data['repo'] = {
                'name': repo.repo_name,
                'organization_name': repo.repo_organization_name,
            }

            key = constants.GITHUB_ISSUE_KEY_FMT.format(**data)
            issues[key] = data

        with etl.db_session_context() as session:
            rows = (
                etl
                .models
                .DataLake
                ._query(session)
                .filter(key__in=tuple(issues.keys()))
            )
            keys_found = set([r.key for r in rows])
            keys_new = set(tuple(issues.keys())) - keys_found
            logger.info(
                f'Load {len(keys_new)}/{len(issues)} new github_issues '
                f'into data_lake.'
            )

            for key in keys_new:
                session.add(
                    etl.models.DataLake(
                        key=key,
                        schema=constants.GITHUB_ISSUE_SCHEMA,
                        data=issues[key],
                    )
                )


def get_max_updated_at(repo):
    sql = """
    SELECT MAX(data ->> 'updated_at')
    FROM data_lake
    WHERE
        schema = :github_issue_schema
        AND (data -> 'repo' ->> 'name') = :repo_name
    """
    params = {
        'github_issue_schema': constants.GITHUB_ISSUE_SCHEMA,
        'repo_name': repo.repo_name,
    }
    with etl.db_session_context() as sess:
        q = sess.execute(sql, params)
        return q.fetchone()[0]


def download_github_issues_for_repo(repo, since=None):
    if since is None:
        # since = '2000-01-01T00:00:00Z'
        since = get_max_updated_at(repo)

    since = arrow.get(since).isoformat()

    # Get the Github repo object
    github_client = (
        etl
        .github
        .create_github_client()
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

    etl.github.execute_github_iterator(iter_issues, GithubIssuesCallback(repo))


def get_watched_repositories():
    with etl.db_session_context() as session:
        return list((
            etl
            .models
            .GitHubRepo
            ._query(session)
            .filter()
        ))
