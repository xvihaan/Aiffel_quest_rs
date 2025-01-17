# agent.py
from nd_graph import create_graph

def run_agent(selected_nodes):
    graph = create_graph()

    # 입력 데이터
    input_data = {
        'case0': selected_nodes,
        'result_node1': [],
        'result_node2': [],
        'result_node3': []
    }

    # 그래프 실행
    result = graph.invoke(input_data)
    return result