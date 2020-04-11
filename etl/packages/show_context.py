from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Following are defaults which can be overridden later on
default_args = {
    'owner': 'dylan',
    'depends_on_past': False,
    'start_date': datetime(2016, 4, 15),
    'email': ['noreply@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'show_context',
    default_args=default_args,
    schedule_interval=timedelta(seconds=10),
)


def log_context(**context):
    import json
    print('\n'+json.dumps(context, indent=2))


PythonOperator(
    task_id="log_context",
    python_callable=log_context,
    provide_context=True,
    dag=dag,
)
