#!env python
import logging
import datetime
import pytz
import gitsu


def etl_event(event, sess):
    actor = event['actor']
    user_ext_id = None if actor is None else actor['id']
    event_ext_id = event['id']

    obj = (
        gitsu
        .models
        .GitHubIssueEvent
        ._query
        .get(
            _session=sess,
            key=event_ext_id
        )
    )
    if obj is not None:
        return False
    obj = (
        gitsu
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
    sess.add(obj)

    logging.info('For issue {}, create event {}'.format(
        event['issue_id'], event['id']))
    return True


def etl_issue_events(dl_events):
    logging.info('ETL events for issue')

    data = dl_events.data
    if data is None:
        logging.info('no events')
    elif isinstance(data, list):
        logging.info('ETL events')
        with gitsu.db_session_context() as sess:
            for event in data:
                etl_event(event, sess)
    else:
        raise Exception('unknown event type {}'.format(type(data)))

    with gitsu.db_session_context() as sess:
        logging.info('update dw_etl_at')
        (
            gitsu
            .models
            .DataLake
            ._query
            .filter(
                key=dl_events.key,
                _session=sess,
            )
            .update(dict(
                dw_etl_at=datetime.datetime.now(pytz.timezone('UTC'))
            ))
        )


def main(**context):
    iterrows = (
        gitsu
        .models
        .DataLake
        ._query
        .filter(
            schema='github_issue_event',
            dw_etl_at__is=None,
        )
    )
    gitsu.etl.map_async(
        etl_issue_events,
        iterrows,
        chunksize=10,
    )


if __name__ == '__main__':
    main()
