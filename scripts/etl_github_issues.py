#!env python
import dateutil
import datetime
import pytz
import functools
import logging 

import gitsu


@functools.lru_cache()
def fetch_single_object(Model, _session=None, **filter_):
	objs = (
		Model
		._query 
		.filter(_session=_session, **filter_)
		.all()
	)
	if len(objs) == 0:
		raise Exception('Value not found {}'.format(data['user']))
	elif len(objs) == 1:
		return objs[0]
	else:
		raise Exception('Too many values found {}'.format(data['user']))	


def etl_issue(dl_issue, session, create_only=True):
	data = dl_issue.data

	objs = list(
		gitsu
		.models
		.GitHubIssue 
		._query
		.filter(
			issue_ext_id=data['id'],
			_session=session
		)
		.all()
	)
	if len(objs) == 0:
		created = True 
		obj = gitsu.models.GitHubIssue(
			issue_ext_id=data['id'],
		)
		logging.info('Creating issue {}'.format(data['id']))

	elif len(objs) == 1:
		obj = objs[0]
		logging.info('Found issue {}'.format(data['id']))
		created = False
		if create_only:
			return created		
	else:
		raise Exception('Returned multiple results')

	obj.issue_state = data['state']
	obj.issue_comments = data['comments']
	obj.issue_created_at = dateutil.parser.parse(data['created_at'])
	obj.issue_closed_at = None if data['closed_at'] is None else dateutil.parser.parse(data['closed_at'])
	obj.issue_updated_at = None if data['updated_at'] is None else dateutil.parser.parse(data['updated_at'])
	obj.issue_is_pull_request = 'pull_request' in data
	obj.issue_events_url =data['events_url']

	user = fetch_single_object(
		gitsu.models.GitHubUser,
		_session=session,		
		user_ext_id=data['user']['id'],
	)
	obj.issue_user_id = user.user_id

	repo = fetch_single_object(
		gitsu.models.GitHubRepo,
		_session=session,
		repo_name=data['repo']['name'],
		repo_organization_name=data['repo']['organization_name']
	)
	obj.issue_repo_id = repo.repo_id

	if created:
		session.add(obj)
	return created


# UPDATE data_lake SET dw_etl_at = NULL WHERE dw_etl_at IS NOT NULL;
iterrows = (
	gitsu
	.models
	.DataLake
	._query
	.filter(
		schema='github_issue',
		dw_etl_at__is=None,
	)
)
total = iterrows.count()
try:
	for i, dl_issue in enumerate(iterrows):
		etl_issue(dl_issue, iterrows.session)

		logging.info('Issue ETL complete {} -- {}/{} ({:.2%})'.format(dl_issue.data['id'], i, total, i/total))
		dl_issue.dw_etl_at = datetime.datetime.now(pytz.timezone('UTC'))
		iterrows.session.commit()
finally:
	iterrows.session.close()




