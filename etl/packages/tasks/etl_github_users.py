#!env python

import logging
import json

import etl
from tasks import constants


logger = logging.getLogger(__name__)


def etl_user(user_data, session):
    obj, created = (
        etl
        .models
        .GitHubUser
        ._query(session)
        .exists_or_create(
            user_ext_id=user_data['id'],
            user_name=user_data['login'],
        )
    )
    if created:
        logger.info('Created User {}'.format(user_data['login']))
    return created


def etl_users_from_issues():
    with etl.db_session_context() as session:
        logger.info('Starting Github Users ETL based on issues')
        iterrows = (
            etl
            .models
            .DataLake
            ._query(session)
            .filter(
                schema=constants.GITHUB_ISSUE_SCHEMA,
                dw_etl_at__is=None,
            )
        )

        unique_user_data = {}
        for dl_issue in iterrows:
            key = dl_issue.key
            data = dl_issue.data
            if isinstance(data, str):
                data = json.loads(data)

            unique_user_data[data['user']['id']] = data['user']

    with etl.db_session_context() as session:
        for user_data in unique_user_data.values():
            etl_user(user_data, session)


def etl_users_from_issue_events():
    with etl.db_session_context() as session:
        logger.info('Starting Github Users ETL based on issue events')
        iterrows = (
            etl
            .models
            .DataLake
            ._query(session)
            .filter(
                schema=constants.GITHUB_ISSUE_EVENTS_SCHEMA,
                dw_etl_at__is=None,
            )
        )

        unique_user_data = {}
        for dl_event in iterrows:
            for evt in dl_event.data:
                ud = evt['actor']
                if ud is not None:
                    unique_user_data[ud['id']] = ud

    with etl.db_session_context() as session:
        for user_data in unique_user_data.values():
            etl_user(user_data, session)


def main(**context):
    logger.info('Starting GitHub Users ELT')
    etl_users_from_issues()
    etl_users_from_issue_events()


if __name__ == '__main__':
    main()
