#!env python
import logging
import github3
import gitsu
import time
import pytz
import dateutil.parser


# TODO: parameterize these
# TODO: SINCE==none should infer from the data
ORG = 'WordPress'
REPO = 'gutenberg'
SINCE = '2000-01-01T00:00'

# Get the Github repo object
repo = (
    github3
    .login(
        token=gitsu.settings.GITHUB_TOKEN,
    )
    .repository(ORG, REPO)
)

# create an issues iterator to access all the issues
iter_issues = repo.issues(
    # YYYY-MM-DDTHH:MM:SSZ
    # since='2018-05-01T00:00:00Z',
    since=(
        dateutil
        .parser
        .parse(SINCE)
        .replace(tzinfo=pytz.UTC)
        .isoformat()
    ),
    sort='updated',
    direction='asc',
    state='all',
)
iter_issues.params.update({
    'page': 1,
    'per_page': 300,
})


CREATED = []


def callback(issue):
    global CREATED

    if isinstance(issue, dict):
        data = issue
    else:
        data = issue._json_data

    data['repo'] = {
        'name': REPO,
        'organization_name': ORG,
    }

    key = 'github_issue_{}'.format(data['id'])
    with gitsu.db_session_context() as sess:
        obj = None
        created = (
            not
            gitsu
            .models
            .DataLake
            ._query
            .exists(_session=sess, key=key)
        )
        if created:
            obj = gitsu.models.DataLake(
                key=key, schema='github_issue', data=data,
            )
            sess.add(obj)
    CREATED.append(created)
    return created


def new_page_callback(iterator, item):
    ratelimit_remaining = getattr(iterator, 'ratelimit_remaining', -1)
    if ratelimit_remaining < 10:
        logging.info('Waiting...')
        time.sleep(15.0 * 60.0)

    global CREATED
    n = len(CREATED)
    s = sum(CREATED)
    if n > 1 and s == 0:
        raise Exception('stop!')
    CREATED = []
    gitsu.github.github_default_new_page_callback(iterator, item)


issues = gitsu.github.github_iterator_results(
    iter_issues, callback=callback, new_page_callback=new_page_callback,
)
