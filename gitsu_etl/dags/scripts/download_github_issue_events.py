#!env python
import logging
import datetime
import pytz
import time
import gitsu


ISSUE_EVENTS_SCHEMA_NAME = 'github_issue_event'


class Event(gitsu.github.github3.models.GitHubCore):
    def __init__(self, json, session):
        """Initialize our basic object.

        Pretty much every object will pass in decoded JSON and a Session.
        """
        # Either or 'session' is an instance of a GitHubCore sub-class or it
        # is a session. In the former case it will have a 'session' attribute.
        # If it doesn't, we can just default to using the passed in session.
        self.session = getattr(session, 'session', session)
        self._json_data = json


def extract_transform_issue_events(issue):
    url = issue.issue_events_url
    logging.info('fetch data from \'{}\''.format(url))
    events = []
    for e in gitsu.github_client._iter(-1, url, Event):
        e._json_data['issue_id'] = getattr(issue, 'issue_ext_id')
        data = e._json_data
        events.append(data)
    return events


def etl_issue_events(issue, session):
    issue_events = extract_transform_issue_events(issue)

    key = '{}_{}'.format(ISSUE_EVENTS_SCHEMA_NAME, issue.issue_ext_id)

    obj = gitsu.models.DataLake._query.get(key=key)
    if obj is None:
        (
            gitsu
            .models
            .DataLake
            ._query
            .exists_or_create(
                _session=session,
                key=key,
                schema=ISSUE_EVENTS_SCHEMA_NAME,
                data=issue_events,
            )
        )
        logging.info('Issue events data stored for {}'.format(key))
    else:
        obj.data = issue_events
        session.commit()
        logging.info('Issue events data updated for {}'.format(key))


def main(update_events_min=None, **context):
    if update_events_min is None:
        update_events_min = (
            datetime.datetime.now(pytz.timezone('UTC'))
            - datetime.timedelta(days=7)
        )

    Model = gitsu.models.GitHubIssue
    filter_clause = Model._query.filter_clause

    clause = (
        filter_clause(
            issue_events_last_loaded_at__lt=update_events_min,
        )
        | filter_clause(
            issue_events_last_loaded_at__is=None,
        )
    )
    with gitsu.db_session_context() as session:
        iterrows = session.query(Model).filter(clause).order_by(Model.issue_updated_at.desc())  # noqa
        n = iterrows.count()
        for i, issue in enumerate(iterrows):
            etl_issue_events(issue, session)
            issue.issue_events_last_loaded_at = (
                datetime.datetime.now(pytz.timezone('UTC'))
            )
            session.commit()

            logging.info('Updated issue {}/{} ({:.3%}) {}'.format(i, n, i / n, issue.issue_updated_at))  # noqa
            logging.info('Github Rate Limit {}'.format(gitsu.github_client.ratelimit_remaining))  # noqa
            if gitsu.github_client.ratelimit_remaining < 10:
                logging.info('Rate Limit Reached, waiting 1 hour')
                time.sleep(3600.0 + 1.0)


if __name__ == '__main__':
    main()
