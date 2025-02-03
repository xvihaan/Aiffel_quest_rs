from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
import json
from ai.demo import DG_LIST

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from segre_search import segre_matrix, get_segregation_value

import re

import os

from h_prompts import *
# .env 파일에서 환경 변수 로드
load_dotenv()

def create_vector_db():
    # Path to save vector DB
    vector_store_path = "./resources/vector/index"

    # Skip creation if vector DB already exists
    if os.path.exists(vector_store_path):
        print("Vector DB already exists. Skipping creation.")
        return

    # Load PDF file
    loader = PyPDFLoader("./resources/docs/IMDG_격리규정안내서.pdf")
    documents = loader.load()

    # Text splitting settings
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )

    # Split document into chunks
    chunks = text_splitter.split_documents(documents)

    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings()

    # Create FAISS vector DB
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Save vector DB
    os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
    vectorstore.save_local(vector_store_path)

    print(f"Vector DB created and saved to {vector_store_path}")


def load_faiss_vector():
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings()

    # Update path to the newly created vector DB location
    vector_store_path = "./resources/vector/index"
    vectorstore = FAISS.load_local(
        vector_store_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore.as_retriever()

def load_segregation_table():
    """Load segregation table from JSON file"""
    try:
        with open("./resources/docs/imdg_격리표.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading segregation table: {e}")
        return None


def load_container_segregation_table():
    """Load container segregation requirements from JSON file"""
    try:
        with open("./resources/docs/imdg_컨테이너적재격리표.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading container segregation table: {e}")
        return None


create_vector_db()
retriever = load_faiss_vector()

segregation_table = load_segregation_table()
container_segregation = load_container_segregation_table()

import re


def str2dict_parser(input_str, type_name):
    """
    문자열에서 'response'와 동적으로 키 데이터를 파싱하여 딕셔너리로 반환.
    다양한 구분자(쉼표, 공백, '와', '및', 'and' 등)를 유연하게 처리.

    Args:
        input_str (str): 입력 문자열
        type_name (str): 동적으로 추출할 키 이름

    Returns:
        dict: {"response": int, "type_name": list}

    Raises:
        ValueError: 입력 형식이 예상과 맞지 않을 때 발생
    """
    # 정규 표현식으로 'response'와 동적 키를 파싱
    pattern = rf"response:\s*(\d),\s*{type_name}:\s*(.*)"
    match = re.match(pattern, input_str.strip(), re.IGNORECASE)

    if not match:
        raise ValueError(f"Unexpected input format. Received: {input_str}")

    # response 값을 정수로 변환
    response = int(match.group(1))
    raw_values = match.group(2).strip()

    # 값이 비어 있을 경우 빈 리스트 반환
    if not raw_values or raw_values.lower() in ["(empty)", "(빈칸)"]:
        return {"response": response, type_name: []}

    # 다양한 구분자(쉼표, '와', '및', 'and', 공백)로 분리
    split_pattern = r"[\s,와및and]+"
    parsed_values = re.split(split_pattern, raw_values)

    # 빈 문자열 제거 후 반환
    parsed_values = [v.strip() for v in parsed_values if v.strip()]
    return {"response": response, type_name: parsed_values}

def setting_node(state):
  print('setting running')
  token = []
  class_list = []
  Context_result = 'empty'
  segre_method_result = 'empty'
  Contain_Segre_result = 'empty'
  return {'token' : token, 'class_list' : class_list, 'Context_result' : Context_result, 'segre_method_result' : segre_method_result, 'Contain_Segre_result' : Contain_Segre_result}

## Domain_check
def node0(state):
  print('node0 running')
  token = []
  user_input = state['user_input']
  llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
  Domain_check_chain = Domain_check_prompt | llm
  Domain_check_input = {"context": retriever, "user_input" : user_input}
  response = Domain_check_chain.invoke(Domain_check_input)
  result = response.content
  print ('result = ',result)
  
  # 임시방편 코드
  result = 'yes'
  return result

## 분기 확인 코드
def CS_Detect0(state):
  print('CS_Detect node running')
  user_input = state['user_input']
  llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
  cs_detect_chain = CS_Detect_prompt | llm
  cs_detect_input = {"user_input": user_input}
  response = cs_detect_chain.invoke(cs_detect_input)
  result = response.content
  print('CS_ result =',result)
  if result == 'Both':
    tokens = state['token'] + [0]
    return {'token' : tokens , 'CS_result' : result}
  else :
    return {'CS_result' : result}

def Both_situ(state):
  token = state['token']
  if 0 in token :
    Ans = 'Both'
    return 'Both'
  else :
    return 'Context'

def Context_node0(state):
  print('Context_node running')
  user_input = state['user_input']
  llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
  Context_chain = Context_prompt | llm
  Context_input = {
            "context": retriever,  # Document 객체 리스트 그대로 전달
            "user_input": user_input,
            "segregation_table": lambda _: json.dumps(segregation_table, ensure_ascii=False) if segregation_table else "No segregation information available",
            "container_segregation": lambda _: json.dumps(container_segregation, ensure_ascii=False) if container_segregation else "No container segregation information available"
        }
  response = Context_chain.invoke(Context_input)
  result = response.content
  print('Context_node running end')
  return {'final_result' : result}

def UN_detect(state):
    """
    Detect UN numbers from user input and add them to the state.
    """
    user_input = state['user_input']

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    UN_detect_chain = UN_detect_prompt | llm
    UN_detect_input = {"user_input": user_input}
    response = UN_detect_chain.invoke(UN_detect_input)
    content0 = response.content

    # Parse LLM response
    try:
        result = str2dict_parser(content0, 'numbers')
        bool_result = result['response']
        unnumbers = result['numbers']

        # Debugging print statements
        print('UN run', unnumbers)

        if bool_result == 0:
            # If the response indicates no UN numbers, do nothing
            return None
        else:
            # Return updated state with detected UN numbers and token
            return {"token": state["token"] + [1], "unnumbers": unnumbers}

    except ValueError as e:
        # Handle parsing errors gracefully
        print(f"Error parsing UN numbers: {e}")
        return None

def get_class_results(numbers):
    """
    입력: numbers (list[str]) - UN 번호 리스트
    출력: class_results (list[str]) - 각 UN 번호의 클래스 결과 리스트
    """
    # 모든 결과를 담을 리스트
    class_results = []

    # DG_LIST에서 데이터 가져오기
    dg_items = DG_LIST.get_all_un_no()

    # 각 un_number에 대해 처리
    for un_number in numbers:
        try:
            # 해당 un_number와 일치하는 데이터 찾기
            oid = next(item for item in dg_items if item["unNumber"] == un_number)["id"]
            item = DG_LIST.find_one(oid)
            # 클래스 결과 추가
            class_results.append(item['class'])
        except StopIteration:
            # un_number가 dg_items에 없는 경우 처리
            print(f"Warning: UN number {un_number} not found.")
            class_results.append(None)  # 없는 경우 None 추가

    return class_results

def get_dg_details(numbers):
    """
    입력: numbers (list[str]) - UN 번호 리스트
    출력: dg_details (list[dict]) - 각 UN 번호의 상세 정보 리스트
    """
    dg_details = []

    # DG_LIST에서 데이터 가져오기
    dg_items = DG_LIST.get_all_un_no()

    for un_number in numbers:
        try:
            # 해당 UN 번호와 일치하는 데이터 찾기
            oid = next(item for item in dg_items if item["unNumber"] == un_number)["id"]
            item = DG_LIST.find_one(oid)
            # 세부 정보 추가
            dg_details.append({
                "unNumber": item['unNumber'],
                "class": item['class'],
                "subsidiaryRisk": item.get('subsidiaryRisk', '-'),
                "packingGroup": item.get('packingGroup', '-'),
                "properShippingName": item['properShippingName']['ko']
            })
        except StopIteration:
            print(f"Warning: UN number {un_number} not found.")
            dg_details.append({
                "unNumber": un_number,
                "class": None,
                "subsidiaryRisk": None,
                "packingGroup": None,
                "properShippingName": None
            })

    return dg_details



def node1(state):
    """
    Node1: Retrieves dangerous goods details and class list for the provided UN numbers.
    """
    print('node1 running')
    token_1 = state["token"]
    if 1 in token_1:
        unnumbers = state["unnumbers"]

        # 각 UN 번호에 대한 클래스 리스트와 상세 정보 가져오기
        class_list = get_class_results(unnumbers)
        dg_details = get_dg_details(unnumbers)
        print(class_list)

        print('node1 is working')
        return {
            'class_list': class_list,
            'dg_details': dg_details
        }
    else:
        pass

def class_Detect(state):
    class_list = state['class_list']
    if len(class_list) > 0:
        return {"class_list" : class_list}
    else:
        print('class_Detect running')
        user_input = state['user_input']
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        class_detect_chain = class_detect_prompt | llm
        class_detect_input = {"user_input": user_input}
        response = class_detect_chain.invoke(class_detect_input)
        content0 = response.content
        result = str2dict_parser(content0, 'class_list')
        bool_result = result['response']
        class_list = result['class_list']
        print(class_list)
        if bool_result == 0:
            pass
        else :
            return {"class_list" : class_list}

def segre_Detect(state):
    print('segre_Detect running')
    user_input = state['user_input']
    
    # LLM 모델과 프롬프트 실행
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    segre_detect_chain = segre_detect_prompt | llm
    segre_detect_input = {"user_input": user_input}
    response = segre_detect_chain.invoke(segre_detect_input)
    
    # 응답 디버깅
    content0 = response.content
    print(f"Response Content: {content0}")
    
    # 파싱 처리
    try:
        result = str2dict_parser(content0, 'why')
        bool_result = result.get('response')  # 'response' 키를 확인
    except Exception as e:
        print(f"Parsing Error: {e}")
        return state  # Parsing 실패 시에도 기본 state 반환
    
    # 결과에 따른 동작
    if bool_result == 0:
        print("No segregation method requested.")
        return state
    else:
        print("Segregation method requested.")
        return {"token": state["token"] + [2]}

segregation_descriptions = {
    "1": {"name": "분리적재 (Away from)", "details": ["최소 3m 이상의 수평거리 유지", "갑판상부/하부 적재 가능", "동일 구획에 적재 가능하나 물리적 분리 필요"]},
    "2": {"name": "격리적재 (Separated from)", "details": ["서로 다른 격실이나 화물창에 적재", "갑판상부 적재 시 최소 6m 이상 수평거리 유지", "수직방향 격리 시 수밀 격벽 필요"]},
    "3": {"name": "1구획실 또는 1화물창 격리적재", "details": ["최소 1개의 완전한 구획실이나 화물창으로 분리", "수평방향으로 최소 12m 이상 거리 유지", "수직방향 격리 불가"]},
    "4": {"name": "1구획실 또는 1화물창 종방향 격리적재", "details": ["최소 24m의 수평거리 유지", "중간에 완전한 구획실이나 화물창 필요", "가장 엄격한 격리 요건"]},
    "X": {"name": "특정 격리규정 확인", "details": ["특정 격리규정을 확인하기 위하여 위험물 목록(DGL)을 참고할 것"]},
    "*": {"name": "제1급 물질 간 격리규정", "details": ["제1급 물질 상호 간의 격리규정에 관하여 제7.2.7.1항을 참조할 것", " 선적 계획 시 제1급 물질의 경우 등급 정보만으로는 부족", "혼적 그룹 정보를 확인하여 계획 수립 필요", "필요시 위험물 전문가의 자문을 구하는 것이 안전"]},
}

from itertools import combinations

def node2(state):
  print('node2 running')
  token_2 = state["token"]

  if 2 in token_2:
    class_list = state["class_list"]
    print('node2 is working')

    if len(class_list) >= 2:
        combinations_list0 = list(combinations(class_list, 2))
        combinations_list = [list(comb) for comb in combinations_list0]
        combinations_list

        final_result = []
        for class_list in combinations_list:
          class_input1 = [class_list[0],'None']
          class_input2 = [class_list[1],'None']
          segre_method_num = get_segregation_value(segre_matrix, class_input1, class_input2)
          Node2_result = segregation_descriptions.get(segre_method_num)
          result = {'class_list' : class_list, 'segre_method_num' : segre_method_num, 'detail' : [Node2_result['name'],Node2_result['details']]  }
          final_result.append(result)

    else:
        segre_method_num = ''
        final_result = ''
    # state - 정수 형태로 method number 저장
    return {'segre_method_result' : final_result, 'segre_method_num' :segre_method_num}
  else :
    pass
  

def Cont_Detect(state):
    print('Cont_Detect running')
    user_input = state['user_input']
    segre_method_result = state['segre_method_result']
    print(f"Segre Method Result: {segre_method_result}")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    Cont_detect_chain = Cont_detect_prompt | llm
    Cont_detect_input = {"user_input": user_input, 'segre_method_result': segre_method_result}
    response = Cont_detect_chain.invoke(Cont_detect_input)
    content0 = response.content
    print(f"Cont_Detect Response: {content0}")
    result = str2dict_parser(content0, 'why')
    bool_result = result['response']
    if bool_result == 0:
        print("No further segregation container option required.")
        pass
    else:
        print("Segregation container option required.")
        return {"token": state["token"] + [3]}

# conditional edge 분기용 함수
def CS_Detect(state):
  print('CS_Detect edge running')
  CS_result = state['CS_result']
  print(CS_result)
  return CS_result


def Cont_Opt_detect(state):
  print('Cont_Opt_detect running')
  token_3 = state["token"]
  if 3 in token_3:
    user_input = state['user_input']
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    Cont_Opt_detect_chain = Cont_Opt_detect_prompt | llm
    Cont_Opt_detect_input = {"user_input": user_input}
    response = Cont_Opt_detect_chain.invoke(Cont_Opt_detect_input)
    content0 = response.content
    # result = str2dict_parser(content0, 'why')
    # bool_result = result['response']

    Cont_Opt = content0
    return {'Cont_Opt' : Cont_Opt}
  else :
    pass

def load_container_segregation_matrix():
    try:
        with open("./resources/docs/imdg_컨테이너적재격리표.json", "r", encoding="utf-8") as f:
            return json.load(f)["segregationMatrix"]
    except Exception as e:
        print(f"Error loading container segregation matrix: {e}")
        return None

segregation_matrix = load_container_segregation_matrix() 

def Cont_result_fnc(segregation_code, segregation_filter,filter_type, deck_position):
  report = ''
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

def parse_variables(input_string):
    """
    주어진 문자열을 파싱하여 변수로 반환. 입력 형식이 맞지 않을 경우 오류 메시지를 출력.
    """
    variables = {}
    lines = input_string.strip().split("\n")
    
    for line in lines:
        # '=' 기호가 없는 경우 건너뜀
        if "=" not in line:
            print(f"Invalid line skipped: {line}")
            continue
        
        try:
            key, value = line.split("=", 1)
            variables[key.strip()] = value.strip().strip("'")
        except ValueError as e:
            print(f"Error parsing line: {line}. Error: {e}")
            continue  # 문제가 있는 줄은 건너뜀
    
    return variables

def node3(state):
  print('node3 running')
  token_3 = state["token"]
  # Segre_method
  if 3 in token_3:
    # 받아오기
    Cont_Opt = state["Cont_Opt"]
    segre_method_num = state["segre_method_num"]

    if segre_method_num == 'X' or segre_method_num == '*':
      Node3_result = 'empty'
    else : 
      # 파싱해서 각 변수에 할당
      parsed = parse_variables(Cont_Opt)
      print(parsed)
      segregation_filter = parsed["segregation_filter"]
      filter_type = parsed["filter_type"]
      deck_position = parsed["deck_position"]
      Node3_result = Cont_result_fnc(segre_method_num, segregation_filter,filter_type, deck_position)
    print('node3 is working')
    return {'Contain_Segre_result' : Node3_result}
  else :
    pass

def final_node(state):
    """
    Final node that aggregates results and generates a final response.
    """
    # State 데이터 가져오기
    user_input = state['user_input']
    segre_method_result = state['segre_method_result']
    Contain_Segre_result = state['Contain_Segre_result']
    segre_method_num = state['segre_method_num']
    dg_details = state.get('dg_details', [])

    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Prompt와 체인 구성
    final_chain = final_prompt | llm

    # 입력 데이터 구성
    final_input = {
        "user_input": user_input,
        "segre_method_result": segre_method_result,
        "Contain_Segre_result": Contain_Segre_result,
        "segre_method_num": segre_method_num,
        "dg_details": dg_details  # 추가된 dangerous goods 세부 정보
    }

    # LLM 호출 및 결과 생성
    response = final_chain.invoke(final_input)
    result = response.content
    return {'final_result': result}