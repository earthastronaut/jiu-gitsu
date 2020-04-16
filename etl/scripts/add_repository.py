#!/usr/local/bin/python
import argparse
import logging

import etl

logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(
    description="Add repository to watch"
)
parser.add_argument(
    'organization',
    help='Name of organization'
)
parser.add_argument(
    'repository',
    help='Name of repository',
)


if __name__ == '__main__':
    pargs = parser.parse_args()
    repository = pargs.repository
    organization = pargs.organization
    # TODO: confirm repository exists?
    with etl.db_session_context() as session:
        obj, created = (
            etl
            .models
            .GitHubRepo
            ._query(session)
            .exists_or_create(
                repo_id=repository,
                repo_name=repository,
                repo_organization_name=organization,
            )
        )
        if created:
            logger.info(f'Repository created {repository}')
        else:
            logger.info(f'Repository found {repository}')
