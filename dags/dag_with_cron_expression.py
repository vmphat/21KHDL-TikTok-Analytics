from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


# Define common arguments
default_args = {
    "owner": "vmphat",
    "retries": 5,
    "retry_delay": timedelta(minutes=1),
}


# Define the DAG
with DAG(
    default_args=default_args,
    dag_id="dag_with_cron_expression_v04",
    start_date=datetime(year=2025, month=1, day=10),
    # Run at 3:00 AM on Monday, Tuesday, and Wednesday
    schedule_interval="0 3 * * Mon-Wed",
) as dag:
    # Define the tasks
    task_1 = BashOperator(
        task_id="task_1",
        bash_command="echo dag with cron expression!",
    )

    # Define the task dependencies
    task_1
