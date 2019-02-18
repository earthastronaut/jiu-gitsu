# Github Issues


Jiu-Gitsu helps you analyze and report on github issues for a repo


# Architecture

1. postgresql -- database backend
1. gitsu-etl -- etl processes to get data in place
1. gitsu-analytics -- analysis processes including notebooks
1. gitsu-web -- frontend visualization


# Installation

1. [Install Docker](https://docs.docker.com/docker-for-mac/install/)
1. [Install Docker-compose](https://docs.docker.com/compose/install/)
1. `docker-compose build` to build the project containers
1. `docker-compose up` to run


# Getting Started

## Data Pipeline

Using `gitsu-etl`, scripts help you download github issues and issue events from a github repo. More scripts take that data then extract, transform, and load (ETL) the data into the postgresql database backend.

## Analytics

Using `gitsu-analytics`, you can start up and run analysis using jupyter notebooks against the postgresql database backend. 

## Dashboard

Using `gitsu-web`, you can build a frontend dashboard with this acting as the
API layer. 

