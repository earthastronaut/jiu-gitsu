from airflow import DAG
from airflow.operators.bash_operator import BashOperator
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
    'hello_world',
    default_args=default_args,
    schedule_interval=timedelta(seconds=10),
)

# t1, t2, t3 and t4 are examples of tasks created using operators

t1 = BashOperator(
    task_id='task_1',
    bash_command='echo "Hello World from Task 1"',
    dag=dag)

t2 = BashOperator(
    task_id='task_2',
    bash_command='echo "Hello World from Task 2"',
    dag=dag)

t3 = BashOperator(
    task_id='task_3',
    bash_command='echo "Hello World from Task 3"',
    dag=dag)

t4 = BashOperator(
    task_id='task_4',
    bash_command='echo "Hello World from Task 4"',
    dag=dag)


def print_params_fn(**kwargs):
    import logging
    logging.info('yay!')
    logging.info(kwargs)
    print('boo!')
    return None


t5 = PythonOperator(
    task_id="task_5",
    python_callable=print_params_fn,
    provide_context=True,
    dag=dag,
)

t1 >> [t2, t3] >> t4 >> t5
