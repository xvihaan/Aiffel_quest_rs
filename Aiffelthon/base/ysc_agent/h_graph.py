from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from h_nodes import *

## state 정의
class MyState(TypedDict):
    user_input: str
    Context_result : str
    CS_result : str
    token : list[int]
    unnumbers : list[str]
    class_list : list[str]
    dg_details : list[str]
    segre_method_num : str
    segre_method_result : str
    Cont_Opt : str
    Contain_Segre_result : str
    graph_log : list[str]
    final_result : str
    domain_result : str


## 그래프 생성
graph = StateGraph(MyState)

## 노드 추가
graph.add_node("setting_node", setting_node)
graph.add_node("Context_node0", Context_node0)
# graph.add_node("node0_result", node0_result)
graph.add_node("CS_Detect0", CS_Detect0)
graph.add_node("CS_Detect", CS_Detect)
graph.add_node("UN_detect", UN_detect)
graph.add_node("node1", node1)
graph.add_node("class_Detect", class_Detect)
graph.add_node("segre_Detect", segre_Detect)
graph.add_node("node2", node2)
graph.add_node("Cont_Detect", Cont_Detect)
graph.add_node("Cont_Opt_detect", Cont_Opt_detect)
graph.add_node("node3", node3)
graph.add_node("final_node", final_node)

## 엣지 추가
graph.add_edge(START, "setting_node")

graph.add_conditional_edges(
    'setting_node',
    node0,
    {
        "yes": "CS_Detect0",
        "no": 'final_node'
    }
)

graph.add_conditional_edges(
    "CS_Detect0",
    CS_Detect,
    {
        "Context": "Context_node0",
        "Logic": "UN_detect"
    }
)


graph.add_edge('UN_detect', "node1")
graph.add_edge('node1', "class_Detect")
graph.add_edge('class_Detect', "segre_Detect")
graph.add_edge('segre_Detect', "node2")
graph.add_edge('node2', "Cont_Detect")
graph.add_edge('Cont_Detect', "Cont_Opt_detect")
graph.add_edge('Cont_Opt_detect', "node3")
graph.add_edge('node3', 'final_node')
graph.add_edge('Context_node0', END)
graph.add_edge('final_node', END)
graph = graph.compile()