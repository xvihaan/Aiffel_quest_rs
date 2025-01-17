# main.py
from nd_agent import run_agent

# 변수 설정
sel_12 = [1, 2]
sel_13 = [1, 3]
sel_23 = [2, 3]

# 원하는 변수 선택
selected_nodes = sel_23  # sel_12, sel_13, sel_23 중 선택

# 실행 및 결과 출력
result = run_agent(selected_nodes)
print("Result:", result)