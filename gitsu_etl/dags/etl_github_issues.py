# 1. download_github_issues.py
# 1. etl_github_repo.py
# 1. etl_github_users.py
# 1. etl_github_issues.py

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import scripts


default_args = {
    'owner': 'dylan',
    'depends_on_past': False,
    'start_date': datetime(2016, 4, 15, 12, 5, 0),
    'email': ['noreply@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'etl_github_issues',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

task_ids = [
    'download_github_issues',
    'etl_github_repo',
    'etl_github_users',
    'etl_github_issues',
]

task_upstream = None
for task_id in task_ids:
    task = PythonOperator(
        dag=dag,
        task_id=task_id,
        python_callable=getattr(scripts, task_id).main,
        provide_context=True,
    )
    if task_upstream is not None:
        task.set_upstream(task_upstream)
    task_upstream = task
