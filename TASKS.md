

## Task-1 db migrations
Implement a tool for running database migrations


## Task-3 implement airflow for etl

update download_events:
 1. download issues
 1. etl issues into db
 1. query db for issues, github_issue.last_events_fetch_at < min or null
 1. get events for issues
 4. store data_lake and update github_issue.last_events_fetch_at

Data Pipeline
1. download_issues.py
1. etl_github_repo.py
1. etl_github_users.py
1. etl_github_issues.py
1. download_github_issue_events.py


## Task-5 create gitsu-web

For API web access.


## Task-7 settings config schema

With the yaml config there's no guarentee of keys being present. How to provide that guarentee? 

Also, misspellings are more difficult to debug. 

## Task-8 pip freeze on build

I want the python requirements files to be flexible so when you do a fresh
build it tries the latest-and-greatest. 

However, I also want to freeze a version and track it in github. The flow I want:

1. `docker-compose build` > generate a pip freeze file
1. check that pip-freeze file into git
1. optional build with specific pip freeze...


## Task-9
