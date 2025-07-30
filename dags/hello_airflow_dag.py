from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def say_hello():
    print("========== HELLO, AIRFLOW IS WORKING ==========")

with DAG(
    dag_id='hello_airflow_dag',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['example'],
) as dag:
    task1 = PythonOperator(
        task_id='say_hello',
        python_callable=say_hello,
    )
