# segregation 격리 요건 보고서 생성 코드(민혁)

import os
import warnings
warnings.filterwarnings('ignore')

# Streamlit을 가장 먼저 import
import streamlit as st

# Streamlit 페이지 설정을 다른 모든 st 호출 전에 실행
st.set_page_config(
    page_title="IMDGGenie.ai",
    page_icon="🤖",
    layout="centered"
)

# Set USER_AGENT environment variable
os.environ["USER_AGENT"] = "IMDGGenie.ai"

import json
from ai.demo import DG_LIST

from dotenv import load_dotenv
load_dotenv()

import base64

# 폰트 적용 함수
def get_base64_encoded_font(font_path):
    with open(font_path, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode('utf-8')

def get_custom_font_css():
    font_base64 = get_base64_encoded_font("./resources/fonts/Freesentation-2ExtraLight.ttf")
    return f"""
    <style>
    @font-face {{
        font-family: 'Freesentation';
        src: url(data:font/ttf;base64,{font_base64}) format('truetype');
    }}

    * {{
        font-family: 'Freesentation', sans-serif !important;
    }}
    </style>
    """

# 폰트 CSS 적용
st.markdown(get_custom_font_css(), unsafe_allow_html=True)


segregation_descriptions = {
    "1": {"name": "분리적재 (Away from)", "details": ["최소 3m 이상의 수평거리 유지", "갑판상부/하부 적재 가능", "동일 구획에 적재 가능하나 물리적 분리 필요"]},
    "2": {"name": "격리적재 (Separated from)", "details": ["서로 다른 격실이나 화물창에 적재", "갑판상부 적재 시 최소 6m 이상 수평거리 유지", "수직방향 격리 시 수밀 격벽 필요"]},
    "3": {"name": "1구획실 또는 1화물창 격리적재", "details": ["최소 1개의 완전한 구획실이나 화물창으로 분리", "수평방향으로 최소 12m 이상 거리 유지", "수직방향 격리 불가"]},
    "4": {"name": "1구획실 또는 1화물창 종방향 격리적재", "details": ["최소 24m의 수평거리 유지", "중간에 완전한 구획실이나 화물창 필요", "가장 엄격한 격리 요건"]},
    "X": {"name": "특정 격리규정 확인", "details": ["특정 격리규정을 확인하기 위하여 위험물 목록(DGL)을 참고할 것"]},
    "*": {"name": "제1급 물질 간 격리규정", "details": ["제1급 물질 상호 간의 격리규정에 관하여 제7.2.7.1항을 참조할 것", " 선적 계획 시 제1급 물질의 경우 등급 정보만으로는 부족", "혼적 그룹 정보를 확인하여 계획 수립 필요", "필요시 위험물 전문가의 자문을 구하는 것이 안전"]},
}

def load_container_segregation_matrix():
    try:
        with open("./resources/docs/imdg_컨테이너적재격리표.json", "r", encoding="utf-8") as f:
            return json.load(f)["segregationMatrix"]
    except Exception as e:
        print(f"Error loading container segregation matrix: {e}")
        return None

def load_segmentation_codes():
    try:
        with open("./resources/docs/imdg_격리표.json", "r", encoding="utf-8") as f:
            return json.load(f)["segregationCodes"]
    except Exception as e:
        print(f"Error loading segregation codes: {e}")
        return {}

def generate_segregation_report_v3(segregation_code, segregation_matrix, segregation_codes, filter_type, deck_position, segregation_filter):
    """
    격리 요건 보고서를 생성하는 함수 (필터 추가)
    """
    if segregation_code not in segregation_codes and segregation_code not in segregation_descriptions:
        return "유효하지 않은 격리 방법 코드입니다."
    
    report = f"## 격리 요건 보고서\n"
    report += f"### 격리 코드: {segregation_code}\n\n"

    # 격리 코드 설명 추가
    if segregation_code in segregation_descriptions:
        segregation_info = segregation_descriptions[segregation_code]
        report += f"**격리 방법**: {segregation_info['name']}\n"
        report += "격리 설명:\n"
        for detail in segregation_info['details']:
            report += f"- {detail}\n"
        report += "\n"

    # segregationMatrix 내용 추가
    if segregation_matrix:
        report += "### 격리 요건:\n"
        for requirement in segregation_matrix["requirements"]:
            if str(requirement["segregationCode"]) == segregation_code:
                # 수직 요건 출력 (Vertical)
                if filter_type in ["All", "Vertical"]:
                    report += "#### 수직 요건 (Vertical)\n"
                    vertical = requirement.get("vertical", {})
                    for key, value in vertical.items():
                        if segregation_filter == "All" or key == segregation_filter:
                            report += f"- {key}: {value['allowance']}\n"

                # 수평 요건 출력 (Horizontal)
                if filter_type in ["All", "Horizontal"]:
                    report += "\n#### 수평 요건 (Horizontal)\n"
                    horizontal = requirement.get("horizontal", {})
                    for deck_key, deck_value in horizontal.items():
                        # deck_position 필터 적용
                        if deck_position == "All" or deck_key == deck_position:
                            report += f"##### {deck_key}:\n"
                            for pair_key, pair_value in deck_value.items():
                                if segregation_filter == "All" or pair_key == segregation_filter:
                                    report += f"- {pair_key}:\n"
                                    if isinstance(pair_value, dict):
                                        for sub_key, sub_value in pair_value.items():
                                            if isinstance(sub_value, dict) and 'content' in sub_value:
                                                report += f"  - {sub_key}: {sub_value['content']}\n"
                                                if 'footnote' in sub_value:
                                                    report += f"    - 주석: {sub_value['footnote']}\n"
                                            else:
                                                report += f"  - {sub_key}: {sub_value}\n"
                                    else:
                                        report += f"  - {pair_value}\n"
                report += "\n"

    return report


# Streamlit UI
menu = st.sidebar.selectbox("Menu", ["Segregator"])

if menu == "Segregator":
    st.title("IMDGGenie.ai Segregator")
    segregation_matrix = load_container_segregation_matrix()
    segregation_codes = load_segmentation_codes()

    segregation_code = st.text_input("격리 방법 코드를 입력하세요 (1-4, X, *):")

        # Deck Position 선택 (기본값: ALL)
    deck_position = st.radio(
        "Deck Position 선택:",
        options=["All", "onDeck", "underDeck"],
        index=0,  # 기본값: ALL
        help="All: 전체 출력, onDeck: 갑판 위, underDeck: 갑판 아래"
    )

    # 새로운 필터 버튼 추가
    segregation_filter = st.radio(
        "격리 필터 선택:",
        options=["All", "closedToClosed", "closedToOpen", "openToOpen"],
        index=0,
        help="All: 전체 출력, closedToClosed: 밀폐형 대 밀폐형, closedToOpen: 밀폐형 대 개방형, openToOpen: 개방형 대 개방형"
    )

    # 기존 필터 버튼 추가
    filter_type = st.radio(
        "필터 선택: 출력할 격리 요건을 선택하세요",
        options=["All", "Vertical", "Horizontal"],
        index=0,
        help="All: 전체 출력, Vertical: 수직 요건만, Horizontal: 수평 요건만"
    )

    if segregation_code:
        report = generate_segregation_report_v3(segregation_code, segregation_matrix, segregation_codes, filter_type, deck_position, segregation_filter)
        st.markdown(report)