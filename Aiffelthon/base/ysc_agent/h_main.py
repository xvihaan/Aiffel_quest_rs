import streamlit as st
from h_graph import graph  # 그래프 정의된 파일명
from pprint import pformat

# Streamlit 페이지 설정
st.set_page_config(
    page_title="IMDG 용수철 이노베이션 RAG System ",
    page_icon="📊",
    layout="wide"
)

# 제목
st.title("IMDG 용수철 이노베이션 RAG Interface")

# 상태 저장 변수
if 'result' not in st.session_state:
    st.session_state['result'] = None
if 'error' not in st.session_state:
    st.session_state['error'] = None

def run_graph():
    """
    그래프 실행 함수. `user_input`의 값이 변경될 때 호출됩니다.
    """
    user_input = st.session_state.get("user_input", "")

    if user_input:
        # MyState 포맷에 맞는 입력 데이터 준비
        input_data = {
            "user_input": user_input,
            "Context_result": "",
            "CS_result": "",
            "token": [],
            "unnumbers": [],
            "class_list": [],
            "segre_method_num": "",
            "segre_method_result": "",
            "Cont_Opt": "segregation_filter = 'closedToClosed'  \n"
                        "filter_type = 'All'  \n"
                        "deck_position = 'All'  ",
            "Contain_Segre_result": "",
            "graph_log": [],
            "final_result": "",
            "domain_result": ""
        }

        # 그래프 실행
        try:
            result = graph.invoke(input_data)

            # 결과 저장
            st.session_state['result'] = {
                "final_result": result.get("final_result", "No final result found."),
                "Contain_Segre_result": result.get("Contain_Segre_result", "No segregation result found."),
                "full_state": result
            }
            st.session_state['error'] = None

        except Exception as e:
            st.session_state['error'] = str(e)
            st.session_state['result'] = None

# 사용자 입력 섹션
st.subheader("User Input for the Graph")
st.text_area(
    "Enter your input for the graph:",
    placeholder="질문 사항을 입력하세요.",
    key="user_input",
    on_change=run_graph
)

# 결과 출력
if st.session_state['result']:
    st.markdown("## Final Result")
    st.success(st.session_state['result']['final_result'])

    st.markdown("## Full State")
    st.code(pformat(st.session_state['result']['full_state']), language="json")

# 오류 메시지 출력
if st.session_state['error']:
    st.error(f"An error occurred during graph execution: {st.session_state['error']}")
