# AIFFEL Campus Online Code Peer Review Templete
- 코더 : 김민혁
- 리뷰어 : 정서연

# PRT(Peer Review Template)
- [ㅇ]  **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
    - 문제에서 요구하는 최종 결과물이 첨부되었는지 확인
        - 중요! 해당 조건을 만족하는 부분을 캡쳐해 근거로 첨부
          3가지 실험의 predict, evaluation 값을 다 도출해내셨고, 이를 시간과 성능을 기준으로 잘 비교하셨습니다.
          데이터 수를 늘려 루브릭 기준에 달성하시면 더 좋을 것 같습니다.
        - 실험1
        - ![image](https://github.com/user-attachments/assets/c9920767-6f3d-4256-aed2-276b14ba8f99)
        - ![image](https://github.com/user-attachments/assets/c3936e08-3c7e-4c38-85e8-120e2792ad0a)

        - 실험2-파인튜닝
        - ![image](https://github.com/user-attachments/assets/b6334577-0677-4b8a-90a3-617a962e7835)
        - ![image](https://github.com/user-attachments/assets/a7c5ad72-94a7-4e56-9a2f-87e2e37d586b)

        - 실험3-bucketing
        - ![image](https://github.com/user-attachments/assets/c61de5e6-420a-4b0f-bb7a-a9d9323a5390)
        - ![image](https://github.com/user-attachments/assets/c5399719-57b8-4bc9-bb9f-13f245b4d379)

        - 최종 결과
        - ![image](https://github.com/user-attachments/assets/7a23b670-0ec4-4564-86e5-c2539919f4ad)

- [ㅇ]  **2. 전체 코드에서 가장 핵심적이거나 가장 복잡하고 이해하기 어려운 부분에 작성된 
주석 또는 doc string을 보고 해당 코드가 잘 이해되었나요?**
    - 해당 코드 블럭을 왜 핵심적이라고 생각하는지 확인
    - 해당 코드 블럭에 doc string/annotation이 달려 있는지 확인
    - 해당 코드의 기능, 존재 이유, 작동 원리 등을 기술했는지 확인
    - 주석을 보고 코드 이해가 잘 되었는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
        - ![image](https://github.com/user-attachments/assets/73843e46-7f9d-4b3e-aabe-7612aa96f174)
        - 실험을 진행하기에 앞서 새로 나온 개념인 bucketing에 대해 개념을 잘 정리하고 시작하였습니다.
        - ![image](https://github.com/user-attachments/assets/44bce90c-60c6-4cb0-be83-198aa2f69588)
        - 파인튜닝에서 파라미터들에 주석을 달아 어떠한 역할을 하는지 자세히 나타내었습니다.
        
- [ㅇ]  **3. 에러가 난 부분을 디버깅하여 문제를 해결한 기록을 남겼거나
새로운 시도 또는 추가 실험을 수행해봤나요?**
    - 문제 원인 및 해결 과정을 잘 기록하였는지 확인
    - 프로젝트 평가 기준에 더해 추가적으로 수행한 나만의 시도, 
    실험이 기록되어 있는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
        - ![image](https://github.com/user-attachments/assets/82550ed0-5205-4c9b-ada5-c6dc07dcd3cc)
        - 데이터 오류가 발생했을 때, 현재 사용 가능한 자원을 확인하고 자원을 줄이기 위해 Batch size를 줄이는 등 다양한 방법을 사용하여 문제를 잘 해결하셨습니다.
        
- [ㅇ]  **4. 회고를 잘 작성했나요?**
    - 주어진 문제를 해결하는 완성된 코드 내지 프로젝트 결과물에 대해
    배운점과 아쉬운점, 느낀점 등이 기록되어 있는지 확인
    - 전체 코드 실행 플로우를 그래프로 그려서 이해를 돕고 있는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
        - ![image](https://github.com/user-attachments/assets/4ff44592-20be-4e97-ad53-0f5226bc72bd)

        
- [ㅇ]  **5. 코드가 간결하고 효율적인가요?**
    - 파이썬 스타일 가이드 (PEP8) 를 준수하였는지 확인
    - 코드 중복을 최소화하고 범용적으로 사용할 수 있도록 함수화/모듈화했는지 확인
        - 중요! 잘 작성되었다고 생각되는 부분을 캡쳐해 근거로 첨부
        - 함수를 사용하여 코드를 간결하게 잘 나타내었습니다.


# 회고(참고 링크 및 코드 개선)
```
# 리뷰어의 회고를 작성합니다.
# 코드 리뷰 시 참고한 링크가 있다면 링크와 간략한 설명을 첨부합니다.
# 코드 리뷰를 통해 개선한 코드가 있다면 코드와 간략한 설명을 첨부합니다.
```
CUBA 오류가 굉장히 자주 발생하는데 현재 사용 가능한 자원의 양을 확인하고 이에 적절히 맞추는 방법 알려주셔서 유익했습니다!
코드들 사이에 "비상비상(이모지)" 이런 내용들이 눈에 확 들어오기도 하고 많은 코드들 속에 리프레쉬 되는 느낌이라 매번 재밌게 보고 있습니다. 다양한 파라미터들을 시도하신게 인상 깊었습니다.
