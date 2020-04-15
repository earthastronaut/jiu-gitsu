#!/usr/local/bin/python
import logging

import arrow

import etl
from tasks import constants


logger = logging.getLogger(__name__)


def save_issues_to_date_lake(github_issues, repo):
    issues = {}
    for data in github_issues:
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

    url = etl.github.create_url_github_repo(
        'issues/',
        repo_organization_name=repo.repo_organization_name,
        repo_name=repo.repo_name,
    )

    params = {
        # since='2018-05-01T00:00:00Z',
        'since': arrow.get(since).isoformat(),
        'sort': 'updated',
        'direction': 'asc',
        'state': 'all',
        'page': 1,
        'per_page': 100,
    }

    callback = etl.github.GithubCallback(save_issues_to_date_lake, repo=repo)
    etl.request_paginated(
        'GET', url,
        callback=callback,
        params=params,
        auth=etl.github.get_github_auth(),
    )


def get_watched_repositories():
    with etl.db_session_context(expire_on_commit=False) as session:
        return (
            session
            .query(etl.models.GitHubRepo)
            .all()
        )
