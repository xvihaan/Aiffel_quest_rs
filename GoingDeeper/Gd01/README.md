# AIFFEL Campus Online Code Peer Review Templete
- 코더 : 김민혁
- 리뷰어 : 박연우


# PRT(Peer Review Template)
- [O]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
    - 문제에서 요구하는 최종 결과물이 첨부되었는지 확인

  
(1) 코퍼스 분석, 전처리, SentencePiece 적용, 토크나이저 구현이 잘 되었고 잘 동작한다.
![image](https://github.com/user-attachments/assets/b771f4d6-135b-4a17-8d63-9b440b10d36b)
![image](https://github.com/user-attachments/assets/186bbeed-a432-4e14-99f6-a27e30a1eb65)
![image](https://github.com/user-attachments/assets/15c3cf86-e707-4bf4-b800-aae3572b9a38)
![image](https://github.com/user-attachments/assets/2af071e4-b9d5-4467-88e3-67f6c4eb7d23)

(2) SentencePiece 토크나이저가 적용된 Text Classifier 모델이 정상적으로 수렴하여 80% 이상의 test accuracy가 확인되었다.
![image](https://github.com/user-attachments/assets/8cedf13d-3154-47f4-9711-45c3f5920e37)

(3) SentencePiece 토크나이저를 활용했을 때의 성능을 다른 토크나이저 혹은 SentencePiece의 다른 옵션의 경우와 비교하여 분석을 체계적으로 진행하였다.
![image](https://github.com/user-attachments/assets/2618dfad-2488-4efd-b489-82ad21e173f1)



    
- [O]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**

SentencePiece 학습 및 SentencePiece Tokenizer 함수 작성, 모델 설계 등 핵심적인 부분을 자신만의 코드로 작성하면서도, 이해하기 쉽게 작성해두었다.
![image](https://github.com/user-attachments/assets/2128f5a0-a0bd-436a-b131-454f37aa8515)
![image](https://github.com/user-attachments/assets/7af9f77d-5a58-4774-9759-111ac6a080b6)
![image](https://github.com/user-attachments/assets/b3f9bf63-dcd6-4a14-b2c5-9a820cd8b5fe)



        
- [O]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**

여러 가지 추가 실험을 진행했다. vocab size, model type 등을 변경하며 결과를 비교하였다.
![image](https://github.com/user-attachments/assets/43dfeae5-a8c3-4a32-9619-6d3e9b96c283)
(1) ![image](https://github.com/user-attachments/assets/4154dc0e-0c6d-45f7-9a63-f11197c420b5)
(2) ![image](https://github.com/user-attachments/assets/302b6c6c-5edf-4f66-a993-477f59dcc1b5)

![image](https://github.com/user-attachments/assets/5979ae6c-5939-43c6-bcd7-6dd86afe844c)

(3) KoNLPy
![image](https://github.com/user-attachments/assets/7f344fc1-d574-4e99-aafb-37a24b71a04d)
![image](https://github.com/user-attachments/assets/4fc634bd-9c7d-4df7-ac09-39d295ecbdb8)
![image](https://github.com/user-attachments/assets/cbf44e7c-5603-4e20-a11f-da26f856e101)


        
- [O]  **4. 회고를 잘 작성했나요?**
   
배운점과 아쉬운점, 느낀점 등이 잘 작성되어 있다. 어떤 부분의 구현이 재미있었고, 어떤 파라미터의 조정이 모델에 영향을 미쳤는지 잘 작성해두었다.
![image](https://github.com/user-attachments/assets/14a9f265-ae27-4b03-85e8-7f286794aa98)


        
- [O]  **5. 코드가 간결하고 효율적인가요?**

  토크나이저 모델 학습, 모델 설계 등의 내용을 함수화/모듈화 하였다.
  이로써 전체 작업(코드 실행) 과정을 매우 간결하게 정리하였고, 한눈에 이해할 수 있게 되었다.
![image](https://github.com/user-attachments/assets/a142b845-d882-416c-8b41-4f0f30321718)
![image](https://github.com/user-attachments/assets/4bf02478-bfb6-44ea-ac34-2a78fe835f2e)




# 회고(참고 링크 및 코드 개선)
```
민혁님의 코드를 리뷰하며 어떤 변인들을 두고 실험을 했는지 주의깊게 보았다.
그리고 전처리 관련 부분에 주석을 자세히 달아 두어서 코드를 복습 및 이해하기 편했다.
전반적으로 예비 리뷰어의 입장을 세심하게 고려하여 주석을 달아 둔 것이 느껴졌다.
더불어 추가 실험 부분에서는, 한 두 번의 시도에 만족하지 않고 더 다양한 실험을 해 보고자 한 열정이 보였다.
개인적으로, 읽는이를 배려하는 마음으로 작성하는 '친절한' 코드가 무엇인지 느껴져 인상깊다.

민혁님 고생하셨습니다!
```
