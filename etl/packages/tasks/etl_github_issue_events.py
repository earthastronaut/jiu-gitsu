#!env python
import logging

import arrow

import etl
from etl import errors
from tasks import constants


logger = logging.getLogger(__name__)


def etl_event(event, session):
    actor = event['actor']
    user_ext_id = None if actor is None else actor['id']
    event_ext_id = event['id']

    obj = (
        etl
        .models
        .GitHubIssueEvent
        ._query(session)
        .get(key=event_ext_id)
    )
    if obj is not None:
        return False
    obj = (
        etl
        .models
        .GitHubIssueEvent(
            event_ext_id=event_ext_id,
            event_issue_ext_id=event['issue_id'],
            event_user_ext_id=user_ext_id,
            event_created_at=event['created_at'],
            event_label=event.get('label', {}).get('name', None),
            event=event.get('event', None),
        )
    )
    session.add(obj)

    logger.info('For issue {}, create event {}'.format(
        event['issue_id'], event['id']))
    return True


def etl_issue_events(data_lake_key):
    logger.info('ETL events for issue')

    with etl.db_session_context() as session:
        obj = (
            etl
            .models
            .DataLake
            ._query(session)
            .get(key=data_lake_key)
        )
        data = obj.data

        if data is None:
            logger.info('no events')
        elif isinstance(data, list):
            for event in data:
                etl_event(event, session)
        else:
            raise errors.ProgrammingError(f'unknown event type {type(data)}')

        logger.info('update dw_etl_at')

        obj.dw_etl_at = arrow.utcnow().datetime


def main(**context):
    with etl.db_session_context() as session:
        data_lake_keys = [
            row[0]
            for row in (
                etl
                .models
                .DataLake
                ._query(session)
                .filter(
                    schema=constants.GITHUB_ISSUE_EVENTS_SCHEMA,
                    dw_etl_at__is=None,
                )
                .values('key')
            )
        ]
    etl.etl.map_async(
        etl_issue_events,
        data_lake_keys,
        chunksize=10,
    )


if __name__ == '__main__':
    main()
