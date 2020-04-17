#!env python
import dateutil
import datetime
import pytz
import logging

import etl
from tasks import constants


logger = logging.getLogger(__name__)


def etl_issue(dl_issue, session, create_only=True):
    data = dl_issue.data

    objs = list(
        etl
        .models
        .GitHubIssue
        ._query(session)
        .filter(issue_ext_id=data['id'])
        .all()
    )
    if len(objs) == 0:
        created = True
        obj = etl.models.GitHubIssue(
            issue_ext_id=data['id'],
        )
        logger.info('Creating issue {}'.format(data['id']))

    elif len(objs) == 1:
        obj = objs[0]
        logger.info('Found issue {}'.format(data['id']))
        created = False
        if create_only:
            return created
    else:
        raise Exception('Returned multiple results')

    obj.issue_state = data['state']
    obj.issue_comments = data['comments']
    obj.issue_created_at = dateutil.parser.parse(data['created_at'])
    obj.issue_closed_at = None if data['closed_at'] is None else dateutil.parser.parse(data['closed_at'])  # noqa
    obj.issue_updated_at = None if data['updated_at'] is None else dateutil.parser.parse(data['updated_at'])  # noqa
    obj.issue_is_pull_request = 'pull_request' in data
    obj.issue_events_url = data['events_url']

    obj.issue_user_ext_id = data['user']['id']
    obj.issue_repo_id = data['repo']['name']

    if created:
        session.add(obj)
    return created


def main(**context):
    with etl.db_session_context() as session:
        # UPDATE data_lake SET dw_etl_at = NULL WHERE dw_etl_at IS NOT NULL;
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
        total = iterrows.count()
        for i, dl_issue in enumerate(iterrows):
            etl_issue(dl_issue, session)

            logger.info(
                'Issue ETL complete {} -- {}/{} ({:.2%})'
                .format(dl_issue.data['id'], i, total, i / total)
            )
            dl_issue.dw_etl_at = datetime.datetime.now(pytz.timezone('UTC'))
            session.commit()


if __name__ == '__main__':
    main()
