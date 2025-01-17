# nodes.py
from typing import List, TypedDict

class MyState2(TypedDict):
    case0: List[int]
    result_node1: list[str]
    result_node2: list[str]
    result_node3: list[str]

def hc_add_case(state: MyState2):
    return {'case0': state['case0']}

def node1(state: MyState2):
    state['result_node1'].append('node1_result')
    print('node1 is run')
    return {"result_node1": 'node1_result'}

def node2(state: MyState2):
    state['result_node2'].append('node2_result')
    print('node2 is run')
    return {"result_node2": 'node2_result'}

def node3(state: MyState2):
    state['result_node3'].append('node3_result')
    print('node3 is run')
    return {"result_node3": 'node3_result'}

def e0(state: MyState2):
    print('node_e is run')
    return state