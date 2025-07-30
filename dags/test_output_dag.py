from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

def write_output():
    file_path = "/tmp/airflow_test_output.txt"
    with open(file_path, "w") as f:
        f.write("Hello, Airflow is working!\n")
    print(f"Message written to {file_path}")

with DAG(
    dag_id='test_output_dag',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['debug'],
) as dag:
    write_task = PythonOperator(
        task_id='write_output_task',
        python_callable=write_output,
    )
