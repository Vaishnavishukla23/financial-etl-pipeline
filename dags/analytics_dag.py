from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
import os

POSTGRES_CONN_ID = "airflow_db"
REPORTS_DIR = "/opt/airflow/dags/reports"
REPORT_FILE = os.path.join(REPORTS_DIR, "fraud_report.csv")

def generate_report():
    """Generate fraud transaction analytics report."""
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    engine = hook.get_sqlalchemy_engine()

    query = """
    SELECT * FROM transactions
    WHERE fraud_flag = TRUE
    ORDER BY timestamp DESC;
    """
    df = pd.read_sql(query, engine)

    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    df.to_csv(REPORT_FILE, index=False)
    print(f"[ANALYTICS] Report saved at: {REPORT_FILE}")

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 7, 27),
    "retries": 1
}

with DAG(
    "analytics_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["analytics", "report"]
) as dag:

    report = PythonOperator(
        task_id="generate_report",
        python_callable=generate_report
    )
