
## Task separate requirements dev

ipython should be in a dev file


## Task implement prefect scheduler

with flow working using flow.run()

No can register with the scheduler. 

Ok, well first you have to get `prefect server start` into containers (and probably not docker-in-docker)

Then you can start the `prefect agent start` client in etl container and register flows. 

register_flows.py script has a watchmedo which will register jobs as updated.


## Task-10 Logging aggregation

can I collect logs from all the services into one location? 

Create a logging service (ha) probably using http://littlebigextra.com/how-to-collect-logs-from-multiple-containers-in-docker-swarm/ and the ELK stack to view logs in elastic search

## Task-4 watched repos

Create a table for watched_repos which includes
the repo and organization names and a boolean for whether watch is enabled.

Then update download_github_issues.main to pull from this table.

Possibly remove this etl_github_repo step


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


## Task-9 db migrations

Implement a tool for running database migrations
db-migrate service using [liquidbase](https://github.com/kilna/liquibase-docker)

only do this once it's needed

