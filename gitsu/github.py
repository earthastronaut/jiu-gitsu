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


def github_default_callback(item):
	return item.as_dict()


def github_default_page_callback(iterator, item):
	if hasattr(item, 'created_at'):
		logging.info('{} created_at {}'.format(item, item.created_at))


def github_iterator_results(iterator, limit=None, callback=github_default_callback, page_callback=github_default_page_callback):
	results = []
	page_cnt = 0
	prev_req_url = None
	for item in iterator:
	    # if the page changed, log progress information
	    req_url = iterator.last_response.url
	    if req_url != prev_req_url:
	        prev_req_url = req_url
	        page_cnt += 1
	        logging.info('Pagination {}'.format(page_cnt))
	        logging.info(req_url)
	        page_callback(iterator, item)

	    # append the issuees
	    results.append(callback(item))
	    if limit and len(results) > limit:
	    	break
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



