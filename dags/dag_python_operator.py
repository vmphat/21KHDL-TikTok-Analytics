from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


# Define common arguments
default_args = {
    "owner": "vmphat",
    "retries": 5,
    "retry_delay": timedelta(minutes=1),
}


def greet(ti) -> None:
    first_name = ti.xcom_pull(task_ids="get_name", key="first_name")
    last_name = ti.xcom_pull(task_ids="get_name", key="last_name")
    age = ti.xcom_pull(task_ids="get_age", key="age")
    print(f"Hello, world! My name is {first_name} {last_name}, "
          f"and I am {age} years old.")


def get_name(ti) -> None:
    ti.xcom_push(key="first_name", value="Phat")
    ti.xcom_push(key="last_name", value="Vu")


def get_age(ti) -> None:
    ti.xcom_push(key="age", value=20)


# Define the DAG
with DAG(
    default_args=default_args,
    dag_id="our_dag_with_python_operator_v06",
    description="Our first dag using python operator",
    start_date=datetime(year=2025, month=1, day=1),
    schedule_interval="@daily",
) as dag:
    # Define the tasks
    task_1 = PythonOperator(
        task_id="greet",
        python_callable=greet,
    )
    task_2 = PythonOperator(
        task_id="get_name",
        python_callable=get_name,
    )
    task_3 = PythonOperator(
        task_id="get_age",
        python_callable=get_age,
    )

    # Define the task dependencies
    [task_2, task_3] >> task_1
