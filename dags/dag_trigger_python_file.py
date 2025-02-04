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
    dag_id="dag_trigger_python_file_v05",
    default_args=default_args,
    start_date=datetime(year=2025, month=1, day=20),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    # Define the tasks
    task_1 = BashOperator(
        task_id="task_1",
        bash_command="cd /mnt/d/__AoIDA-Project/src && python main.py",
    )

    # Define the task dependencies
    task_1
