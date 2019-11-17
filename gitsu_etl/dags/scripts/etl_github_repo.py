#!env python
import logging
import gitsu


def etl_github_repo(repo):
    obj, created = (
        gitsu
        .models
        .GitHubRepo
        ._query
        .exists_or_create(
            repo_id=repo['name'],
            repo_name=repo['name'],
            repo_organization_name=repo['organization_name'],
        )
    )
    if created:
        logging.info('Created REPO {}'.format(repo))
    return created


iterrows = (
    gitsu
    .models
    .DataLake
    ._query
    .filter(
        schema='github_issue',
        dw_etl_at__is=None,
    )
    .all()
)

repos = []
for dl_issue in iterrows:
    repo = dl_issue.data['repo']
    if repo not in repos:
        etl_github_repo(repo)
        repos.append(repo)
