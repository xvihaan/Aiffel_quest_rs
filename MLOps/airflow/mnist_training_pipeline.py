from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum

# Airflow 기본 설정
local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1, tzinfo=local_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    'mnist_training_pipeline',
    default_args=default_args,
    description='MNIST 학습 및 하이퍼파라미터 튜닝 파이프라인',
    schedule_interval='@daily',
    catchup=False,
    tags=['mnist'],
) as dag:

    # 데이터 전처리 함수
    def load_and_preprocess_data():
        import tensorflow as tf
        import numpy as np
        import ssl

        # SSL 인증 오류 해결
        ssl._create_default_https_context = ssl._create_unverified_context

        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        x_train = x_train.astype(np.float32) / 255.0
        x_test = x_test.astype(np.float32) / 255.0
        x_train = np.expand_dims(x_train, axis=-1)
        x_test = np.expand_dims(x_test, axis=-1)
        y_train = y_train.astype(np.int64)
        y_test = y_test.astype(np.int64)

        print("데이터 로드 및 전처리 완료!")
        return (x_train, y_train), (x_test, y_test)

    # 모델 학습 함수
    def train_model():
        import wandb
        import tensorflow as tf
        from wandb.integration.keras import WandbMetricsLogger

        wandb.login()
        wandb.init(
            project="mnist-classification",
            entity="your_wandb_username",
            config={
                "learning_rate": 0.001,
                "conv1_filters": 32,
                "conv2_filters": 64,
                "epochs": 10
            }
        )

        (x_train, y_train), (x_test, y_test) = load_and_preprocess_data()
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])
        
        history = model.fit(
            x_train, y_train,
            epochs=10,
            validation_data=(x_test, y_test),
            callbacks=[WandbMetricsLogger()]
        )

        test_loss, test_accuracy = model.evaluate(x_test, y_test)
        print(f"Test accuracy: {test_accuracy:.4f}")

        wandb.log({"test_loss": test_loss, "test_accuracy": test_accuracy})
        wandb.finish()

    # 하이퍼파라미터 스윕 함수
    def hyperparameter_sweep():
        import wandb

        wandb.login()
        sweep_config = {
            'method': 'random',
            'metric': {'name': 'val_accuracy', 'goal': 'maximize'},
            'parameters': {
                'learning_rate': {'values': [0.001, 0.0001]},
                'conv1_filters': {'values': [32, 64]},
                'conv2_filters': {'values': [64, 128]},
                'epochs': {'values': [5, 10]}
            }
        }

        sweep_id = wandb.sweep(sweep_config, project="mnist-sweep")

        def sweep_train():
            import tensorflow as tf
            from wandb.integration.keras import WandbMetricsLogger

            wandb.init()
            (x_train, y_train), (x_test, y_test) = load_and_preprocess_data()
            model = tf.keras.Sequential([
                tf.keras.layers.Conv2D(wandb.config.conv1_filters, (3, 3), activation='relu', input_shape=(28, 28, 1)),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(wandb.config.conv2_filters, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(10, activation='softmax')
            ])

            model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=wandb.config.learning_rate),
                          loss='sparse_categorical_crossentropy', metrics=['accuracy'])
            model.fit(x_train, y_train, epochs=wandb.config.epochs, validation_data=(x_test, y_test))
            wandb.finish()

        wandb.agent(sweep_id, sweep_train, synchronous=True)

    # Airflow 태스크 정의
    preprocessing_task = PythonOperator(
        task_id='load_and_preprocess_data',
        python_callable=load_and_preprocess_data,
        dag=dag
    )

    training_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
        dag=dag
    )

    hyperparameter_tuning_task = PythonOperator(
        task_id='hyperparameter_tuning',
        python_callable=hyperparameter_sweep,
        dag=dag
    )

    # 작업 의존성 설정
    preprocessing_task >> training_task >> hyperparameter_tuning_task