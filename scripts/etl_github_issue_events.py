#!env python
import logging
import datetime
import pytz
import gitsu


def etl_event(event):
	actor = event['actor']
	user_ext_id = None if actor is None else actor['id']

	_, created = (
		gitsu
		.models
		.GitHubIssueEvent
		._query
		.exists_or_create(
			event_ext_id=event['id'],
			event_issue_ext_id=event['issue_id'],
			event_user_ext_id=user_ext_id,
			event_created_at=event['created_at'],
			event_label=event.get('label', {}).get('name', None),
		)
	)
	if created:
		logging.info('For issue {}, create event {}'.format(event['issue_id'], event['id']))
	return created


def etl_issue_events(dl_events):
	logging.info('ETL events for issue')

	data = dl_events.data
	if data is None:
		logging.info('no events')
	elif isinstance(data, list):
		logging.info('ETL events')		
		for event in data:
			etl_event(event)
	else:
		raise Exception('unknown event type {}'.format(type(events)))

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



if __name__ == '__main__':
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
