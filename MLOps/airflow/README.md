# `new` DAG 파일 'mnist_training_pipeline' 설명

## 📌 파일 개요
•	이 Python 파일은 Apache Airflow에서 사용하는 **DAG(워크플로우)**를 정의합니다.

•	DAG는 “Hello, Airflow!“와 “Hello, World!” 메시지를 순차적으로 출력하는 간단한 작업을 포함합니다.

### 1. 라이브러리 임포트
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
```

### 2. 기본 인자 설정
```python
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
```

•	retries: 실패 시 재시도 횟수 (1회).

•	retry_delay: 재시도 간격 (5분).

### 3. DAG 정의
```python
with DAG(
    'mnist_training_pipeline',
    default_args=default_args,
    description='MNIST 학습 파이프라인',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['mnist'],
) as dag:
```
•	schedule_interval: 매일 한 번 실행.

•	start_date: 시작 날짜는 2024년 1월 1일.

•	catchup=False: 과거 실행 건너뜀.

### 4. 작업함수 정의 및 의존성 설정
```python
def print_hello():
    print("Hello, Airflow!")

def print_world():
    print("Hello, World!")
hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
)

world_task = PythonOperator(
    task_id='print_world',
    python_callable=print_world,
)

hello_task >> world_task
```
•	hello_task: print_hello 함수 실행.

•	world_task: print_world 함수 실행.

•	hello_task >> world_task: hello_task가 완료된 후 world_task가 실행됩니다.
