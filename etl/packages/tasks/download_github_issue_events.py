#!env python
import logging

import arrow

import etl
from etl.conf import settings
from tasks import constants

logger = logging.getLogger(__name__)


def load_issue_events(issue, issue_events):
    issue_id = issue['issue_ext_id']

    events = []
    for data in issue_events:
        data['issue_id'] = issue_id
        events.append(data)

    key = constants.GITHUB_ISSUE_EVENTS_KEY_FMT.format(issue_id=issue_id)
    with etl.db_session_context() as session:
        obj = (
            etl
            .models
            .DataLake
            ._query(session)
            .get(key=key)
        )
        obj_found = (obj is not None)
        if obj_found:
            # update
            obj.data = events
        else:
            obj = etl.models.DataLake(
                key=key,
                schema=constants.GITHUB_ISSUE_EVENTS_SCHEMA,
                data=events,
            )
            session.add(obj)

        s = 'updated' if obj_found else 'created'
        logger.info(f'Issue events data {s} for {key}')

        now = arrow.utcnow()

        # TODO: the sqlalchemy update was trying to force session.commit()
        # so I decided to by-pass. In future try to use something in sqlalchemy
        assert etl.models.GitHubIssue.__tablename__ == 'github_issue'
        sql = """
        UPDATE github_issue
        SET
            issue_events_last_loaded_at = :value
        WHERE
            issue_ext_id = :issue_ext_id
        """

        params = {
            'value': now.datetime.isoformat(),
            'issue_ext_id': issue_id,
        }

        session.execute(sql, params)

        md = issue['metadata']
        i = md['runtime_index']
        n = md['total_count']
        p = md['runtime_precent']
        logger.info(f'Updated issue {i}/{n} ({p:.3%}) {now}')


class GithubIssueEventsStore:

    def __init__(self):
        self.events = []

    def __call__(self, events):
        self.events.extend(events)


def download_and_save_issue_events(issue):
    url = issue['issue_events_url']
    params = {
        'page': 1,
        'per_page': 100,
    }
    events_store = GithubIssueEventsStore()
    etl.request_paginated(
        'GET', url,
        callback=etl.github.GithubCallback(events_store),
        params=params,
        auth=etl.github.get_github_auth(),
    )
    load_issue_events(issue, events_store.events)


def get_github_issues_to_update(update_events_min):
    Model = etl.models.GitHubIssue
    filter_clause = Model._query.filter_clause
    clause = (
        filter_clause(issue_events_last_loaded_at__lt=update_events_min.datetime)  # noqa
        | filter_clause(issue_events_last_loaded_at__is=None)
    )
    columns = [
        'issue_ext_id',
        'issue_events_url',
    ]
    with etl.db_session_context() as session:
        query = (
            session
            .query(Model)
            .filter(clause)
        )
        count = query.count()
        iterrows = (
            query
            .order_by(Model.issue_updated_at.desc())
            .values(*[getattr(Model, c) for c in columns])
        )
        issues = []
        for values in iterrows:
            issue = dict(zip(columns, values))
            issue['metadata'] = {
                'runtime_index': len(issues),
                'total_count': count,
                'runtime_precent': len(issues) / count,
            }
            issues.append(issue)
        return issues


def main(update_events_min=None):
    if update_events_min is None:
        update_events_min = (
            arrow
            .utcnow()
            .shift(seconds=(-1 * settings.GITHUB_ISSUE_EVENTS_UPDATE_FREQUENCY))
        )
    issues = get_github_issues_to_update(update_events_min)
    # TODO: with multiprocessing.Pool() as pool:
    for i, issue in enumerate(issues):
        download_and_save_issue_events(issue)


if __name__ == '__main__':
    main()
