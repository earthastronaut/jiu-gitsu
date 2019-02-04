#!env python
import logging
import gitsu


def etl_user(user_data):
    obj, created = (
        gitsu
        .models
        .GitHubUser
        ._query
        .exists_or_create(
            user_ext_id=user_data['id'],
            user_name=user_data['login'],
        )
    )
    if created:
        logging.info('Created User {}'.format(user_data['login']))
    return created


iterrows = (
    gitsu
    .models
    .DataLake
    ._query
    .filter(
        schema='github_issue',
        dw_etl_at__is=None,
    )
    .all()
)


unique_user_data = {}
for dl_issue in iterrows:
    ud = dl_issue.data['user']
    unique_user_data[ud['id']] = ud

for user_data in unique_user_data.values():
    etl_user(user_data)
