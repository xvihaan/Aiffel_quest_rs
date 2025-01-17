import streamlit as st
import json
from ai.demo import DG_LIST, generate_stream_response
from segre_search import segre_matrix, get_segregation_value, load_container_segregation_matrix, load_segmentation_codes
import re


segregation_descriptions = {
    "1": {"name": "분리적재 (Away from)", "details": ["최소 3m 이상의 수평거리 유지", "갑판상부/하부 적재 가능", "동일 구획에 적재 가능하나 물리적 분리 필요"]},
    "2": {"name": "격리적재 (Separated from)", "details": ["서로 다른 격실이나 화물창에 적재", "갑판상부 적재 시 최소 6m 이상 수평거리 유지", "수직방향 격리 시 수밀 격벽 필요"]},
    "3": {"name": "1구획실 또는 1화물창 격리적재", "details": ["최소 1개의 완전한 구획실이나 화물창으로 분리", "수평방향으로 최소 12m 이상 거리 유지", "수직방향 격리 불가"]},
    "4": {"name": "1구획실 또는 1화물창 종방향 격리적재", "details": ["최소 24m의 수평거리 유지", "중간에 완전한 구획실이나 화물창 필요", "가장 엄격한 격리 요건"]},
    "X": {"name": "특정 격리규정 확인", "details": ["특정 격리규정을 확인하기 위하여 위험물 목록(DGL)을 참고할 것"]},
    "*": {"name": "제1급 물질 간 격리규정", "details": ["제1급 물질 상호 간의 격리규정에 관하여 제7.2.7.1항을 참조할 것", " 선적 계획 시 제1급 물질의 경우 등급 정보만으로는 부족", "혼적 그룹 정보를 확인하여 계획 수립 필요", "필요시 위험물 전문가의 자문을 구하는 것이 안전"]},
}

# 필요한 함수들 로드
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
st.title("IMDGGenie.ai Segregator")

# 위험물 목록
dg_items = DG_LIST.get_all_un_no()
dg_options = [(f"{item['unNumber']} - {item['psn']}", item["unNumber"]) for item in dg_items]
dg_labels = [label for label, _ in dg_options]

# class 저장용
good1_class = []
good2_class = []

# 컨테이너 정보 입력
left, right = st.columns(2)

# 컨테이너 1
with left:
    st.subheader("컨테이너 1")
    cntr_type_1 = st.selectbox(label="Container Type", options=["Closed", "Open"], key="cntr_type_1")
    selected_label_1 = st.selectbox("UN 번호", options=dg_labels, index=None, placeholder="Select UN number", key="un_number_1")
    if selected_label_1:
        un_number_1 = next(value for label, value in dg_options if selected_label_1 == label)
        oid_1 = next(item for item in dg_items if item["unNumber"] == un_number_1)["id"]
        item_1 = DG_LIST.find_one(oid_1)
        good1_class.append(str(item_1['class']))
        good1_class.append(str(item_1.get('subsidiaryRisk', '-')))
        st.write("#### 위험물 정보")
        st.write(f"**UN 번호:** {item_1['unNumber']}")
        st.write(f"**급 (Class):** {item_1['class']}")
        st.write(f"**부 위험성:** {item_1.get('subsidiaryRisk', '-')}")
        st.write(f"**포장 등급:** {item_1.get('packingGroup', '-')}")
        st.write(f"**정식운송품명 (PSN):** {item_1['properShippingName']['ko']}")

# 컨테이너 2
with right:
    st.subheader("컨테이너 2")
    cntr_type_2 = st.selectbox(label="Container Type", options=["Closed", "Open"], key="cntr_type_2")
    selected_label_2 = st.selectbox("UN 번호", options=dg_labels, index=None, placeholder="Select UN number", key="un_number_2")
    if selected_label_2:
        un_number_2 = next(value for label, value in dg_options if selected_label_2 == label)
        oid_2 = next(item for item in dg_items if item["unNumber"] == un_number_2)["id"]
        item_2 = DG_LIST.find_one(oid_2)
        good2_class.append(str(item_2['class']))
        good2_class.append(str(item_2.get('subsidiaryRisk', '-')))
        st.write("#### 위험물 정보")
        st.write(f"**UN 번호:** {item_2['unNumber']}")
        st.write(f"**급 (Class):** {item_2['class']}")
        st.write(f"**부 위험성:** {item_2.get('subsidiaryRisk', '-')}")
        st.write(f"**포장 등급:** {item_2.get('packingGroup', '-')}")
        st.write(f"**정식운송품명 (PSN):** {item_2['properShippingName']['ko']}")

st.divider()

# Segregation method 선택
segregation_matrix = load_container_segregation_matrix()  # 격리 행렬 로드
segregation_codes = load_segmentation_codes()  # 격리 코드 로드

# Segre_number 계산
Segre_number = get_segregation_value(segre_matrix, good1_class, good2_class)

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


# 버튼 클릭 시 보고서 생성
if st.button("Analyze Segregation Requirements"):

    # Segre_number 계산
    Segre_number = get_segregation_value(segre_matrix, good1_class, good2_class)

    if Segre_number:
        # Segre_number를 segregation_code로 설정
        segregation_code = Segre_number
        
        # 보고서 생성
        report = generate_segregation_report_v3(
            segregation_code, 
            segregation_matrix, 
            segregation_codes, 
            filter_type, 
            deck_position, 
            segregation_filter
        )
        
        # 보고서 출력
        st.markdown(report)  # 마크다운 형식으로 출력
    else:
        st.error("Segregation requirements could not be determined. Please check the container information.")

