#!env python
import logging

import etl


logger = logging.getLogger(__name__)


def etl_user(user_data):
    obj, created = (
        etl
        .models
        .GitHubUser
        ._query
        .exists_or_create(
            user_ext_id=user_data['id'],
            user_name=user_data['login'],
        )
    )
    if created:
        logger.info('Created User {}'.format(user_data['login']))
    return created


def etl_users_from_issues():
    logger.info('Starting Github Users ETL based on issues')
    iterrows = (
        etl
        .models
        .DataLake
        ._query
        .filter(
            schema='github_issue',
            dw_etl_at__is=None,
        )
    )

    unique_user_data = {}
    for dl_issue in iterrows:
        ud = dl_issue.data['user']
        unique_user_data[ud['id']] = ud

    for user_data in unique_user_data.values():
        etl_user(user_data)


def etl_users_from_issue_events():
    logger.info('Starting Github Users ETL based on issue events')
    iterrows = (
        etl
        .models
        .DataLake
        ._query
        .filter(
            schema='github_issue_event',
            dw_etl_at__is=None,
        )
    )

    unique_user_data = {}
    for dl_event in iterrows:
        for evt in dl_event.data:
            ud = evt['actor']
            if ud is not None:
                unique_user_data[ud['id']] = ud

    for user_data in unique_user_data.values():
        etl_user(user_data)


def main(**context):
    logger.info('Starting GitHub Users ELT')
    etl_users_from_issues()
    etl_users_from_issue_events()


if __name__ == '__main__':
    main()
