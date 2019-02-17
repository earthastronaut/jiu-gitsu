import os
import csv
import logging 
import json

import github3

from gitsu.conf import settings
from gitsu import etl


github_client = (
	github3
    .login(
        token=settings.GITHUB_TOKEN,
    )
)


# def repo_events(repo, number=-1, etag=None, **params):
#     url = repo._build_url('events', base_url=repo._api)
#     params = repo_issue_params(milestone, state, assignee, mentioned,
#                                labels, sort, direction, since)
#     return repo._iter(int(number), url, events.Event, params=params, etag=etag)
# 	pass 

# def repo_issue_params(milestone=None,
#                       state=None,
#                       assignee=None,
#                       mentioned=None,
#                       labels=None,
#                       sort=None,
#                       direction=None,
#                       since=None,
#                       number=-1,
#                       etag=None):
#     """Validate and filter issue method parameters in one place."""
#     params = {'assignee': assignee, 'mentioned': mentioned}
#     if milestone in ('*', 'none') or isinstance(milestone, int):
#         params['milestone'] = milestone
#     Repository._remove_none(params)
#     params.update(
#         issues.issue_params(
#             None, state, labels, sort, direction, since
#         )
#     )
#     return params




def github_default_callback(item):
	return item


def github_default_new_page_callback(iterator, item):
	if hasattr(item, 'updated_at'):
		logging.info('{} updated_at {}'.format(item, item.updated_at))
	if hasattr(item, 'created_at'):
		logging.info('{} created_at {}'.format(item, item.created_at))


def github_iterator_results(iterator, limit=None, callback=github_default_callback, new_page_callback=github_default_new_page_callback):
	results = []
	page_cnt = 0
	prev_req_url = None
	try:
		for item in iterator:
		    # if the page changed, log progress information
		    req_url = iterator.last_response.url
		    if req_url != prev_req_url:
		        prev_req_url = req_url
		        page_cnt += 1
		        logging.info('Pagination {}'.format(page_cnt))
		        logging.info('rate limit remaining {}'.format(getattr(iterator, 'ratelimit_remaining', -1)))
		        logging.info(req_url)
		        new_page_callback(iterator, item)

		    # append the issuees
		    results.append(callback(item))
		    if limit and len(results) > limit:
		    	break
	except Exception as e:
		logging.error(str(e))
	return results


def github_store_results(iterator_results, filename):
	# write issues out to file
	if not os.path.isdir(settings.DATA_PATH):
	    os.makedirs(settings.DATA_PATH)

	fp = os.path.join(settings.DATA_PATH, filename)
	with open(fp, 'w') as f:
	    json.dump(iterator_results, f)


def github_read_results(filename):
	fp = os.path.join(settings.DATA_PATH, filename)
	with open(fp) as f:
		return json.load(f)


def github_store_results_csv(normalized_results, filename):
	fp_out = os.path.join(
		settings.DATA_PATH,
		filename,
	)
	with open(fp_out, 'w') as fptr:
		fields = normalized_results[0].keys()
		wtr = csv.DictWriter(fptr, fields)
		wtr.writeheader()
		wtr.writerows(normalized_results)	



