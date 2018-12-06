#!env python
GITHUB_TOKEN = 'a292a9e6589851f265d22d54ddf9cbdf86df88e7'
ORG = 'WordPress'
REPO = 'gutenberg'
OUTPUT_FILENAME = '{}_{}_issues.json'.format(ORG, REPO)
ISSUES_SINCE = '2018-01-01' 

import os
import logging

import json
import github3
import pandas as pd
import gitsu


# Get the Github repo object
repo = (
    github3
    .login(
        token=GITHUB_TOKEN,
    )
    .repository(ORG, REPO)
)

# create an issues iterator to access all the issues
iter_issues = repo.issues(
    #YYYY-MM-DDTHH:MM:SSZ    
    since=pd.Timestamp(ISSUES_SINCE).strftime('%Y-%m-%dT%H:%M:%SZ'),
    sort='created',
    direction='asc',
)

# loop the iterator and get all issues
issues = []
page_cnt = 0
prev_req_url = None
for issue in iter_issues:
    # if the page changed, log progress information
    req_url = iter_issues.last_response.url
    if req_url != prev_req_url:
        prev_req_url = req_url
        page_cnt += 1
        logging.info('Pagination {}'.format(page_cnt))
        logging.info(req_url)
        logging.info('Issues created {}'.format(issue.created_at.date().isoformat()))

    # append the issuees
    issues.append(issue.as_dict())

# write issues out to file
if not os.path.isdir(gitsu.settings.DATA_PATH):
    os.makedirs(gitsu.settings.DATA_PATH)
fp = os.path.join(gitsu.settings.DATA_PATH, OUTPUT_FILENAME)
with open(fp, 'w') as f:
    json.dump(issues, f)
logging.info('done!')

