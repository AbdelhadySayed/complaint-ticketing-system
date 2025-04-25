from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from bart_retrain_mlflow import check_for_retraining, finetune_bart

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=30),
}

dag = DAG(
    'monthly_bart_retraining',
    default_args=default_args,
    description='Monthly retraining of BART model for complaint responses',
    schedule_interval='0 0 1 * *',  # Runs at 00:00 on the 1st day of each month
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['ml', 'retraining'],
)

def check_data_availability():
    try:
        check_for_retraining()
        return "Data available for retraining"
    except ValueError as e:
        return f"Skipping retraining: {str(e)}"

check_data_task = PythonOperator(
    task_id='check_data_availability',
    python_callable=check_data_availability,
    dag=dag,
)

retrain_task = PythonOperator(
    task_id='retrain_bart_model',
    python_callable=finetune_bart,
    dag=dag,
)

# Set up dependencies
check_data_task >> retrain_task