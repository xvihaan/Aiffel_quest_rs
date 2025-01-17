# graph.py
from langgraph.graph import StateGraph, START, END
from typing import List
from nd_nodes import hc_add_case, node1, node2, node3, e0, MyState2

def create_graph():
    graph = StateGraph(MyState2)

    # 노드 추가
    graph.add_node('case', hc_add_case)
    graph.add_node('N1', node1)
    graph.add_node('N2', node2)
    graph.add_node('N3', node3)
    graph.add_node("e", e0)

    # START에서 'case' 노드로 엣지 추가
    graph.add_edge(START, "case")

    # 동적으로 노드 선택
    def route_bc_or_cd(state: MyState2) -> list[int]:
        active_nodes = []
        if 1 in state["case0"]:
            active_nodes.append("N1")
        if 2 in state["case0"]:
            active_nodes.append("N2")
        if 3 in state["case0"]:
            active_nodes.append("N3")
        return active_nodes

    intermediates = ['N1', 'N2', 'N3']

    # 조건부 엣지 추가
    graph.add_conditional_edges(
        "case",
        route_bc_or_cd,
        intermediates
    )

    for node in intermediates:
        graph.add_edge(node, "e")

    # 최종 노드 연결
    graph.add_edge("e", END)

    return graph.compile()