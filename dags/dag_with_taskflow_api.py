from datetime import datetime, timedelta
from airflow.decorators import dag, task


# Define common arguments
default_args = {
    "owner": "vmphat",
    "retries": 5,
    "retry_delay": timedelta(minutes=1),
}


# Define the DAG
@dag(dag_id="dag_with_taskflow_api_v02",
     default_args=default_args,
     start_date=datetime(year=2025, month=1, day=1),
     schedule_interval="@daily",)
def hello_world_etl():

    @task(multiple_outputs=True)
    def get_name() -> dict:
        return {"first_name": "Phat", "last_name": "Vu"}

    @task()
    def get_age() -> int:
        return 19

    @task()
    def greet(first_name: str, last_name: str, age: int) -> None:
        print(f"Hello, world! My name is {first_name} {last_name}, "
              f"and I am {age} years old.")

    # Define the task dependencies
    name_dict = get_name()
    age = get_age()
    greet(first_name=name_dict["first_name"],
          last_name=name_dict["last_name"], age=age)


# Create a DAG object
greet_dag = hello_world_etl()
