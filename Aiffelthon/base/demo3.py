# 개선(실험중)된 context. 데이터가 없어서 잠시 중단.

import os
import warnings
import json
from ai.demo import DG_LIST, generate_stream_response
warnings.filterwarnings('ignore')

import streamlit as st

st.set_page_config(
    page_title="IMDGGenie.ai",
    page_icon="🤖",
    layout="centered"
)

WORKFLOW_STEPS = {
    "1": "제품 입고",
    "2": "MSDS 확인",
    "3": "위험물 포장",
    "4": "선적 서류 작성, 승인 요청",
    "5": "위험물 검사 신청",
    "6": "컨테이너 배차",
    "7": "컨테이너 장입",
    "8": "검사증 조회",
    "9": "수출 진행"
}

os.environ["USER_AGENT"] = "IMDGGenie.ai"

from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fuzzywuzzy import process
import random
import re

# 세션 상태 초기화 (파일 상단, st.set_page_config 아래에 추가)
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

def create_vector_db():
    """Vector DB 생성 함수"""
    vector_store_path = "./resources/vector/index"
    pdf_path = "./resources/docs/IMDG_격리규정안내서.pdf"
    
    try:
        if os.path.exists(vector_store_path):
            print("Vector DB already exists. Skipping creation.")
            embeddings = OpenAIEmbeddings()
            FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
            return
    except Exception as e:
        print(f"Error loading existing vector DB: {e}")
        print("Creating new Vector DB...")
        
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)

            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(splits, embeddings)
            
            os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
            vectorstore.save_local(vector_store_path)
            print("Vector DB created successfully.")
        except Exception as e:
            print(f"Error creating vector DB: {e}")
            raise

def load_faiss_vector():
    """FAISS 벡터 로드 함수"""
    vector_store_path = "./resources/vector/index"
    try:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        return vectorstore.as_retriever(search_kwargs={"k": 2})
    except Exception as e:
        print(f"Error loading FAISS vector: {e}")
        raise

def load_dangerous_goods_from_json():
    """IMDG 위험물 목록 JSON 파일 로드"""
    file_path = '/Users/minhyeok/Desktop/PROJECT/Aiffelthon/aiffelthon_tys_imdg/tys/baseline/app/resources/docs/imdg_위험물목록.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("dangerousGoodsList", [])
    except Exception as e:
        print(f"Error loading IMDG dangerous goods list: {e}")
        return []

def search_dangerous_goods(dg_json_list, query_terms, response_text=None, user_input=None):
    """위험물 목록에서 검색어와 관련된 항목 찾기 - UN 번호 우선 매칭 개선 버전"""
    if not dg_json_list:
        return []
    
    found_items = []
    
    def extract_un_numbers(text):
        if not text:
            return set()
        patterns = [
            r'UN\s*(\d{4})',      # UN 1234
            r'UN(\d{4})',         # UN1234
            r'유엔\s*(\d{4})',     # 유엔 1234
            r'유엔번호\s*(\d{4})',  # 유엔번호 1234
            r'UN No\s*:\s*(\d{4})',# UN No: 1234
            r'UN Number\s*:\s*(\d{4})'  # UN Number: 1234
        ]
        numbers = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            numbers.update(matches)
        return numbers

    # 1단계: UN 번호 직접 매칭
    un_numbers = set()
    # 질문에서 UN 번호 추출
    if user_input:
        un_numbers.update(extract_un_numbers(user_input))
    # 답변에서 UN 번호 추출
    if response_text:
        un_numbers.update(extract_un_numbers(response_text))
    
    # UN 번호로 직접 매칭되는 항목 먼저 찾기
    if un_numbers:
        for un_number in un_numbers:
            for item in dg_json_list:
                if item.get('unNumber', '') == un_number:
                    found_items.append(item)
                    break  # 해당 UN 번호 항목을 찾으면 중단
    
    # 2단계: 키워드 기반 카테고리 매칭
    if len(found_items) < 5:  # UN 번호 매칭 후 남은 공간이 있는 경우에만
        categories = {}
        for item in dg_json_list:
            if item in found_items:  # 이미 찾은 항목은 건너뛰기
                continue
                
            score = 0
            psn_ko = item.get('properShippingName', {}).get('ko', '').lower()
            psn_en = item.get('properShippingName', {}).get('en', '').lower()
            
            # 키워드 매칭 점수 계산
            for term in query_terms:
                term = term.lower()
                if term in psn_ko or term in psn_en:
                    score += 10
                if response_text and term in response_text.lower():
                    score += 5

            if score >= 10:
                category_name = None
                for key in ["탄", "가스", "산", "염"]:
                    if key in psn_ko:
                        category_name = psn_ko.split(key)[0] + key
                        break
                
                if category_name:
                    if category_name not in categories:
                        categories[category_name] = []
                    categories[category_name].append((item, score))
        
        # 카테고리별 대표 항목 추가
        for category, items in categories.items():
            if len(found_items) >= 5:
                break
            items.sort(key=lambda x: x[1], reverse=True)
            if items[0][0] not in found_items:
                found_items.append(items[0][0])
    
    return found_items

def generate_dynamic_follow_up_questions(user_input, context):
    """AI 모델을 사용하여 동적으로 후속 질문 생성"""
    prompt = f"""
    Given the context and the user input, generate three follow-up questions that are relevant to the topic.

    Context:
    {context}

    User Input:
    {user_input}

    Follow-up Questions:
    1.
    2.
    3.
    """
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    response = model(prompt)
    
    follow_up_questions = response.split("\n")
    return [q.strip() for q in follow_up_questions if q.strip()]

# Create sidebar menu
menu = st.sidebar.selectbox("Menu", ["Context", "Segregator"])

# 세션 상태 초기화
if 'asked_questions' not in st.session_state:
    st.session_state.asked_questions = set()

if menu == "Context":
    st.title("IMDGGenie.ai Context Chatbot")

    try:
        create_vector_db()
        retriever = load_faiss_vector()
        
        dangerous_goods_json = load_dangerous_goods_from_json()

        if not dangerous_goods_json:
            st.error("위험물 목록을 불러오는데 실패했습니다.")
            st.stop()

        if 'user_input' not in st.session_state:
            st.session_state.user_input = ""

        user_input = st.text_input("Enter your question about IMDG Code:", st.session_state.user_input)

        if user_input:
            keywords = [word.strip() for word in user_input.split() if len(word.strip()) > 1]
            
            # 개선된 질문 생성
            refine_template = """
            You are an IMDG Code expert. Please improve the given question to be more specific and professional.
            Make it more detailed while maintaining the original intent.

            Original Question:
            {question}

            Instructions:
            1. Enhance the question to be more specific and technical
            2. Include relevant IMDG Code terminology
            3. Focus on safety and regulatory aspects
            4. Keep the improved question in Korean
            5. Maintain the core meaning of the original question

            Improved Question:
            """

            refine_prompt = ChatPromptTemplate.from_template(refine_template)
            refine_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
            refine_chain = refine_prompt | refine_model | StrOutputParser()

            # 개선된 질문 생성
            refined_question = refine_chain.invoke({"question": user_input})

            # 메인 답변을 위한 chain 정의
            template = """
            You are a senior IMDG Code expert with extensive experience. Please provide a detailed and structured answer to the question.

            Context:
            {context}

            Dangerous Goods List:
            {dangerous_goods_list}

            Question: 
            {question}

            Instructions:
            1. Answer in Korean with a professional and detailed manner
            2. Structure your response with clear sections using markdown
            3. Include the following elements in your answer:
               - Main explanation with relevant IMDG Code references
               - Specific requirements and procedures
               - Safety considerations and precautions
               - Practical implementation guidelines
               - Related regulations and standards

            Format your response as:

            ### 📌 답변
            [Detailed main answer with structured sections]

            ### 🔍 세부 요구사항
            - [Specific requirements]
            - [Detailed procedures]
            - [Safety measures]

            ### ⚠️ 주의사항
            - [Important precautions]
            - [Critical considerations]

            ### 📋 참고사항
            - [Additional relevant information]
            - [IMDG Code references]

            ### 후속 질문:
            1. [Specific follow-up question about detailed requirements]
            2. [Follow-up question about practical implementation]
            3. [Follow-up question about safety considerations]
            """

            prompt = ChatPromptTemplate.from_template(template)
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
            
            chain = (
                {
                    "context": retriever,
                    "question": RunnablePassthrough(),
                    "dangerous_goods_list": lambda _: json.dumps(found_dangerous_goods, ensure_ascii=False)[:1000] if found_dangerous_goods else "No matching dangerous goods found"
                }
                | prompt
                | model
                | StrOutputParser()
            )

            # 개선된 질문 표시
            st.write("---")
            st.write(f"**원래 질문**: {user_input}")
            st.write(f"**개선 질문**: {refined_question}")
            st.write("---")

            # 위험물 검색 및 답변 생성
            found_dangerous_goods = search_dangerous_goods(
                dangerous_goods_json, 
                keywords + refined_question.split(), 
                st.session_state.full_response,
                user_input
            )

            # 메인 답변 표시
            response_container = st.empty()
            st.session_state.full_response = ""
            
            # Generate streaming response
            for chunk in chain.stream(refined_question):
                st.session_state.full_response += chunk
                response_container.markdown(st.session_state.full_response)
            
            try:
                # 답변에서 후속 질문 추출
                response_text = st.session_state.full_response
                if "### 후속 질문:" in response_text:
                    questions_section = response_text.split("### 후속 질문:")[1].strip()
                    follow_up_questions = []
                    
                    # 번호가 매겨진 질문들을 추출
                    for line in questions_section.split("\n"):
                        if line.strip().startswith(("1.", "2.", "3.")):
                            question = line.strip().split(". ", 1)[1]
                            if question:  # 빈 문자열이 아닌 경우만 추가
                                follow_up_questions.append(question)
                    
                    if follow_up_questions:
                        st.write("---")
                        
                        # 3개의 컬럼 생성
                        cols = st.columns(3)
                        
                        # 각 컬럼에 버튼 배치
                        for idx, (col, question) in enumerate(zip(cols, follow_up_questions)):
                            with col:
                                if st.button(f"👉 \n{question}", key=f"btn_{idx}", use_container_width=True):
                                    st.session_state.user_input = question
                                    st.experimental_rerun()
            
            except Exception as e:
                print(f"Error processing recommended questions: {e}")

            # 위험물 정보 표시
            if found_dangerous_goods:
                st.write("---")
                st.write("### 📦 관련 위험물 정보")
                for item in found_dangerous_goods:
                    with st.expander(f"🔍 {item['properShippingName']['ko']} (UN {item['unNumber']})"):
                        st.markdown(f"""
                        ### ⦿ 위험물 정보:
                        - **UN 번호**: {item.get('unNumber', '정보 없음')}
                        - **위험물 분류**: {item.get('class', '정보 없음')}
                        - **부위험성**: {item.get('subsidiaryRisk', '정보 없음')}
                        - **용기등급**: {item.get('packingGroup', '정보 없음')}
                        
                        #### 품목명
                        - 🇰🇷 {item['properShippingName'].get('ko', '정보 없음')}
                        - 🇺🇸 {item['properShippingName'].get('en', '정보 없음')}
                        
                        #### 특별 규정
                        {item.get('specialProvisions', '특별 규정 없음')}
                        
                        #### 포장 규정
                        - **포장 지침**: {item.get('packing', {}).get('instruction', '정보 없음')}
                        - **특별 포장 규정**: {item.get('packing', {}).get('provisions', '정보 없음')}
                        """)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if menu == "Segregator":
    st.title("IMDGGenie.ai Segregator")

    # Select deck position
    deck_position = st.selectbox("Deck Position", ["Below Deck", "Above Deck"])

    # List of dangerous goods
    dg_items = DG_LIST.get_all_un_no()
    dg_options = [(f"{item['unNumber']} - {item['psn']}", item["unNumber"]) for item in dg_items]
    dg_labels = [label for label, _ in dg_options]

    left, right = st.columns(2) 
    with left:
        st.subheader("Container 1")
        cntr_type_1 = st.selectbox(label="Container Type", options=["Closed", "Open"], key="cntr_type_1")
        selected_label_1 = st.selectbox("UN Number", options=dg_labels, index=None, placeholder="Select UN number", key="un_number_1")
        if selected_label_1:
            un_number_1 = next(value for label, value in dg_options if selected_label_1 == label)
            oid_1 = next(item for item in dg_items if item["unNumber"] == un_number_1)["id"]
            item_1 = DG_LIST.find_one(oid_1)

            st.write("#### Dangerous Goods Information")
            st.write(f"**UN Number:** {item_1['unNumber']}")
            st.write(f"**Class:** {item_1['class']}")
            st.write(f"**Subsidiary Risk:** {item_1.get('subsidiaryRisk', '-')}")
            st.write(f"**Packing Group:** {item_1.get('packingGroup', '-')}")
            st.write(f"**Proper Shipping Name (PSN):** {item_1['properShippingName']['ko']}")
    with right:
        st.subheader("Container 2")
        cntr_type_2 = st.selectbox(label="Container Type", options=["Closed", "Open"], key="cntr_type_2")
        selected_label_2 = st.selectbox("UN Number", options=dg_labels, index=None, placeholder="Select UN number", key="un_number_2")
        if selected_label_2:
            un_number_2 = next(value for label, value in dg_options if selected_label_2 == label)
            oid_2 = next(item for item in dg_items if item["unNumber"] == un_number_2)["id"]
            item_2 = DG_LIST.find_one(oid_2)

            st.write("#### Dangerous Goods Information")
            st.write(f"**UN Number:** {item_2['unNumber']}")
            st.write(f"**Class:** {item_2['class']}")
            st.write(f"**Subsidiary Risk:** {item_2.get('subsidiaryRisk', '-')}")
            st.write(f"**Packing Group:** {item_2.get('packingGroup', '-')}")
            st.write(f"**Proper Shipping Name (PSN):** {item_2['properShippingName']['ko']}")

    st.divider()

    if st.button("Analyze Segregation Requirements"):
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


