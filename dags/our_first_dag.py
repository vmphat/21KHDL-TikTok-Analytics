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
    dag_id="our_first_dag_v5",
    description="This is our first dag that we write in Airflow",
    start_date=datetime(year=2025, month=1, day=1, hour=0),
    schedule_interval="@daily",
    default_args=default_args,
) as dag:
    # Define the tasks
    task_1 = BashOperator(
        task_id="first_task",
        bash_command="echo hello world, this is the first task",
    )
    task_2 = BashOperator(
        task_id="second_task",
        bash_command="echo hey, this is the second task which is running after the task_1",
    )
    task_3 = BashOperator(
        task_id="third_task",
        bash_command="echo hey, I am task3 and I am running after task1 at the same time as task2",
    )

    # Define the task dependencies

    # Set task dependencies method 1
    # task_1.set_downstream(task_2)
    # task_1.set_downstream(task_3)

    # Set task dependencies method 2
    # task_1 >> task_2
    # task_1 >> task_3

    # Set task dependencies method 3
    task_1 >> [task_2, task_3]
