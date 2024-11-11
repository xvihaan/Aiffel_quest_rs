from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# 기본 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    'mnist_training_pipeline',
    default_args=default_args,
    description='MNIST 학습 파이프라인',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['mnist'],
) as dag:

    # Python 작업 함수 정의
    def print_hello():
        print("Hello, Airflow!")

    def print_world():
        print("Hello, World!")

    # PythonOperator로 작업 정의
    hello_task = PythonOperator(
        task_id='print_hello',
        python_callable=print_hello,
    )

    world_task = PythonOperator(
        task_id='print_world',
        python_callable=print_world,
    )

    # 작업 의존성 설정
    hello_task >> world_task
