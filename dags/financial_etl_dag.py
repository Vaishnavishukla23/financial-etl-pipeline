from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os
import psycopg2
import csv

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 28),
}

dag = DAG(
    dag_id='financial_etl_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
)

# Paths
BASE_DIR = '/opt/airflow/dags/data'
os.makedirs(BASE_DIR, exist_ok=True)
RAW_CSV = os.path.join(BASE_DIR, 'transactions.csv')
TRANSFORMED_CSV = os.path.join(BASE_DIR, 'transformed_transactions.csv')

def ingest_data():
    data = {
        'transaction_id': [1, 2, 3],
        'user_id': [101, 102, 103],
        'amount': [250.75, 125.0, 320.4],
        'currency': ['USD', 'EUR', 'USD'],
        'timestamp': [
            '2025-07-27 17:34:45.984881',
            '2025-07-27 17:34:45.984899',
            '2025-07-27 17:34:45.984900'
        ],
        'merchant': ['Amazon', 'Flipkart', 'Apple'],
        'fraud_flag': [False, True, False]
    }
    df = pd.DataFrame(data)
    df.to_csv(RAW_CSV, index=False)

def transform_data():
    df = pd.read_csv(RAW_CSV)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['amount_inr'] = df.apply(lambda row: row['amount'] * 83 if row['currency'] == 'USD'
                                 else row['amount'] * 90 if row['currency'] == 'EUR'
                                 else row['amount'], axis=1)
    df.to_csv(TRANSFORMED_CSV, index=False)

def load_data_to_postgres():
    conn = psycopg2.connect(
        host='postgres',
        database='airflow',
        user='airflow',
        password='airflow'
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INT,
            user_id INT,
            amount FLOAT,
            currency VARCHAR(10),
            timestamp TIMESTAMP,
            merchant VARCHAR(50),
            fraud_flag BOOLEAN,
            amount_inr FLOAT
        );
    """)
    conn.commit()

    df = pd.read_csv(TRANSFORMED_CSV)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO transactions (transaction_id, user_id, amount, currency, timestamp, merchant, fraud_flag, amount_inr)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(row))
    conn.commit()
    cursor.close()
    conn.close()

def aggregate_monthly_summary():
    conn = psycopg2.connect(
        host='postgres',
        database='airflow',
        user='airflow',
        password='airflow'
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_summary (
            month VARCHAR(10),
            merchant VARCHAR(50),
            total_amount_inr FLOAT
        );
    """)
    conn.commit()

    cursor.execute("""
        INSERT INTO monthly_summary (month, merchant, total_amount_inr)
        SELECT TO_CHAR(timestamp, 'YYYY-MM') AS month,
               merchant,
               SUM(amount_inr)
        FROM transactions
        GROUP BY month, merchant;
    """)
    conn.commit()
    cursor.close()
    conn.close()

def export_summary_to_csv():
    conn = psycopg2.connect(
        host='postgres',
        database='airflow',
        user='airflow',
        password='airflow'
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM monthly_summary;")
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    os.makedirs('/opt/airflow/exported_data', exist_ok=True)
    with open('/opt/airflow/exported_data/monthly_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    cursor.close()
    conn.close()

# Define tasks
t1 = PythonOperator(task_id='ingest_data', python_callable=ingest_data, dag=dag)
t2 = PythonOperator(task_id='transform_data', python_callable=transform_data, dag=dag)
t3 = PythonOperator(task_id='load_data_to_postgres', python_callable=load_data_to_postgres, dag=dag)
t4 = PythonOperator(task_id='aggregate_monthly_summary', python_callable=aggregate_monthly_summary, dag=dag)
t5 = PythonOperator(task_id='export_summary_to_csv', python_callable=export_summary_to_csv, dag=dag)

# Set dependencies
t1 >> t2 >> t3 >> t4 >> t5
