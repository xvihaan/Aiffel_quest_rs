import tensorflow as tf
from tensorflow.keras import layers, models
from datetime import datetime

# 모델 생성 함수
def create_model(learning_rate=0.001, conv1_filters=32, conv2_filters=64):
    model = models.Sequential([
        layers.Conv2D(conv1_filters, (3, 3), activation='relu', input_shape=(28, 28, 1)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(conv2_filters, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    print("모델 생성 및 컴파일 완료!")
    return model

# 데이터 로드 및 전처리 함수
def load_and_preprocess_data():
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train.astype('float32') / 255.0
    x_test = x_test.astype('float32') / 255.0
    x_train = x_train[..., tf.newaxis]
    x_test = x_test[..., tf.newaxis]
    return (x_train, y_train), (x_test, y_test)

# 모델 학습 및 저장 함수
def train_and_save_model():
    (x_train, y_train), (x_test, y_test) = load_and_preprocess_data()
    model = create_model()
    model.fit(x_train, y_train, epochs=5, validation_data=(x_test, y_test))
    
    # 모델 저장
    model.save("mnist_model.h5")
    print("모델이 'mnist_model.h5'로 저장되었습니다.")

if __name__ == "__main__":
    train_and_save_model()