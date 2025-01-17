import json

import streamlit as st

from ai.demo import DG_LIST, generate_stream_response

# 페이지 제목
st.title("IMDGGenie.ai Segregator")

# 적재 위치 선택
deck_position = st.selectbox("적재 위치", ["갑판하부", "갑판상부"])

# 위험물 목록
dg_items = DG_LIST.get_all_un_no()
# Selectbox 옵션 라벨 - UN 번호 맵핑
dg_options = [(f"{item["unNumber"]} - {item["psn"]}", item["unNumber"]) for item in dg_items]
# Selectbox 옵션 라벨
dg_labels = [label for label, _ in dg_options]

# 컨테이너 정보 입력
left, right = st.columns(2)
# 컨테이너 1
with left:
    st.subheader("컨테이너 1")
    # 컨테이너 형태 선택
    cntr_type_1 = st.selectbox(label="컨테이너 형태", options=["밀폐형", "개방형"], key="cntr_type_1")
    # UN 번호 선택
    selected_label_1 = st.selectbox("UN 번호", options=dg_labels, index=None, placeholder="Select UN number", key="un_number_1")
    if selected_label_1:
        # 라벨 - UN 번호 맵핑 리스트에서 실제 UN 번호 찾기
        un_number_1 = next(value for label, value in dg_options if selected_label_1 == label)
        # --- UN 번호로 조회
        # item_1 = DG_LIST.find_by_un_no(un_number_1)
        # --- MongoDB oid로 조회
        oid_1 = next(item for item in dg_items if item["unNumber"] == un_number_1)["id"]
        item_1 = DG_LIST.find_one(oid_1)

        # 위험물 정보 출력
        st.write("#### 위험물 정보")
        st.write(f"**UN 번호:** {item_1["unNumber"]}")
        st.write(f"**급 (Class):** {item_1["class"]}")
        st.write(f"**부 위험성:** {item_1.get("subsidiaryRisk", "-")}")
        st.write(f"**포장 등급:** {item_1.get("packingGroup", "-")}")
        st.write(f"**정식운송품명 (PSN):** {item_1["properShippingName"]["ko"]}")
# 컨테이너 2
with right:
    st.subheader("컨테이너 2")
    # 컨테이너 형태 선택
    cntr_type_2 = st.selectbox(label="컨테이너 형태", options=["밀폐형", "개방형"], key="cntr_type_2")
    # UN 번호 선택
    selected_label_2 = st.selectbox("UN 번호", options=dg_labels, index=None, placeholder="Select UN number", key="un_number_2")
    if selected_label_2:
        # 라벨 - UN 번호 맵핑 리스트에서 실제 UN 번호 찾기
        un_number_2 = next(value for label, value in dg_options if selected_label_2 == label)
        # --- UN 번호로 조회
        # item_2 = DG_LIST.find_by_un_no(un_number_2)
        # --- MongoDB oid로 조회
        oid_2 = next(item for item in dg_items if item["unNumber"] == un_number_2)["id"]
        item_2 = DG_LIST.find_one(oid_2)

        # 위험물 정보 출력
        st.write("#### 위험물 정보")
        st.write(f"**UN 번호:** {item_2["unNumber"]}")
        st.write(f"**급 (Class):** {item_2["class"]}")
        st.write(f"**부 위험성:** {item_2.get("subsidiaryRisk", "-")}")
        st.write(f"**포장 등급:** {item_2.get("packingGroup", "-")}")
        st.write(f"**정식운송품명 (PSN):** {item_2["properShippingName"]["ko"]}")

st.divider()

# 분석 버튼
if st.button("격리 요건 분석"):
    # 그래프 실행
    input = {
        "containers": [
            {
                "un_number": un_number_1,
                "cntr_type": cntr_type_1
            },
            {
                "un_number": un_number_2,
                "cntr_type": cntr_type_2
            }
        ],
        "deck_position": deck_position
    }
    response_stream = generate_stream_response(input)

    # 결과 출력
    container = st.container(border=True)
    result = ""
    with container.empty():
        for data in response_stream:
            dict = json.loads(data)
            status = dict["status"]
            chunk = dict["data"]
            if status == "processing":
                st.markdown(chunk)
            elif status == "streaming":
                result += chunk
                st.markdown(result)
