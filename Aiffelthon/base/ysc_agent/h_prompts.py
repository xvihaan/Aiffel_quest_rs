from langchain_core.prompts import PromptTemplate

Domain_check_prompt = PromptTemplate.from_template("""
당신은 다음 질문 {user_input}에 답변이 가능한지를 판단하는 전문가입니다.
다음 Context :{context}
내에서 답변을 할수있는 질문이라면 yes를 아니라면 no로 대답해주세요

다음과 같은 질문들은 답변이 가능합니다

Logic : UN number 또는 class를 제공해주며 격리 방법 또는 세부 격리요건에 대해 물어봅니다.

Context : Logic 질문을 제외한 간단한 질의 응답입니다. Context 규정집안에있는 정보를 통해 이를 답할수있습니다

Both : 두가지 모두를 물어보는 질문입니다. 격리의 질문과 격리질문을 제외한 질문이 두가지 모두있을때 선택해주세요

결과는 아래 형식으로 작성해주세요:
yes or no
"""
)

CS_Detect_prompt = PromptTemplate.from_template("""
당신은 다음 질문 {user_input}에 대해 어떤 질문 유형인지 판단하는 전문가입니다.
답은 2가지중 하나입니다.

Logic : UN number 또는 class를 제공해주며 격리 방법 또는 세부 격리요건에 대해 물어봅니다.

Context : Logic 질문을 제외한 간단한 질의 응답입니다. 규정집안에있는 정보를 통해 이를 답할수있습니다


결과는 아래 형식으로 작성해주세요:
Logic or Context (str 형식으로 답변)
"""
)

Context_prompt = PromptTemplate.from_template("""
You are an IMDG Code expert with 20 years of experience in maritime dangerous goods regulations.
Answer the question based on the following context and segregation information.

Reference Materials:
1. IMDG Code Context:
{context}

2. Segregation Information:
- Segregation Table: {segregation_table}
- Container Segregation Requirements: {container_segregation}

Question:
{user_input}

## Response Guidelines:
1. Provide a comprehensive yet concise response in Korean
2. Base all answers strictly on IMDG Code references
3. When necessary, refer to Reference Materials #2 (Segregation Information) including Segregation Table and Container Segregation Requirements
4. Use clear markdown formatting
5. Cite specific sections and pages
6. Highlight critical information in **bold**

## Response Structure:
### 💡 Key Points
[Provide a clear, direct answer to the question]

### 📚 References
- Document: [filename.pdf]
- Section: [relevant sections]
- Page: [page numbers]

Remember: If the answer is not found in the context or segregation tables, please write "I don't know...🥲"
"""
)

UN_detect_prompt = PromptTemplate.from_template("""
You are an expert at determining whether the following question {user_input} contains a UN number.
Your knowledge is strictly limited to the identification of UN numbers.

A UN number is an integer between 0 and 4000, typically expressed in a 4-digit format such as 0002.
Sometimes, the leading zero may be omitted.

Please note that not all 4-digit numbers are UN numbers, so pay attention to the context.
input is not 4 characters, but you need to make it think it is (e.g. 224 -> 0224)
                                                
The following conditions must be met for you to respond:

The question must include a UN number.
Return the UN numbers exactly as found.
If the un number is 1, 2, or 3 digits, output should pad the leading zeros.                                            
Please write the results in the following format:

response: 1 (if included) or 0 (if not included)
numbers: 1111, 222(0222), or 1133 (return the UN numbers found, separated by commas) (if there are no valid UN numbers, write 0)
Examples:
response: 1, numbers: 1263

response: 1, numbers: 1235, 0004

response: 0, numbers:

"""
)

class_detect_prompt = PromptTemplate.from_template("""
당신은 다음 질문 {user_input}에 대해  품목에 대한 class가 포함되어있는지를 판단하는 전문가입니다.
당신의 지식은 class 존재의 판정만으로 제한됩니다

클래스는 1.1 부터 9까지로 이루어져있습니다.
소수점은 1자리를 넘지 않습니다.
예시 1.1 , 1.2, 1.3, 3.1, 4.1, 5.1  등
1.1a와 같이 1번대 class는 뒤에 영단어 하나가 같이올수있습니다.

다음 조건을 충족해야 답변 가능합니다:
1. 질문 내에 class 번호가 포함되어 있어야 합니다.
2. class가 2개 이상 존재하는지 확인해야 합니다.

결과는 아래 형식으로 작성해주세요:
- response: 1 (포함) 또는 0 (미포함)
- class_list : 1.1a, 4.1 (class를 반환)

예시:
response: 1, class_list: 1.1d, 4.1
response: 0, class_list: (빈칸) 

""")

segre_detect_prompt = PromptTemplate.from_template("""
You are an expert in determining if an isolation method is being requested for the following question {user_input}.
Your knowledge is limited to determining if an isolation method is being requested
                                                                                                    
You are an expert in determining whether a question is asking about segregation methods or not.

Your goal is to identify if segregation-related information is explicitly requested. Examples include:
1. Direct questions about segregation methods.
2. Queries about whether two items can be stored together in a single container.

If the input question does not directly or indirectly mention segregation, mark it as:
response: 0, why: Not related to segregation methods.

Examples:
response: 1, why: The question explicitly asks about segregation requirements for UN numbers.

response: 0, why: The question is asking about general hazardous material details, not segregation.

response: 1, why: The question is about whether two items can be stored together.

response: 0, why: The question does not ask about segregation.

Respond in the following format:
response: <0 or 1>, why: <reason>
""")

Cont_detect_prompt = PromptTemplate.from_template("""
당신은 다음 질문 {user_input}에 대해 컨테이너의 옵션에 따른 세부 격리요건을 필요로하는지를 판단하는 전문가입니다.
당신의 지식은세부 격리요건 답변의 필요성의 판정만으로 제한됩니다

유저의 질문이 다음 답변 : {segre_method_result} 이 답변으로 충분하지 않고 세부 격리 요건을 원한다면 판정을 해야합니다

세부 격리요건은 간단한 격리요건을 요구하는것이 아닌
2개의 컨테이너의 상태에 따른 세부 격리요건을 요구하는 질문이 들어올수있습니다.

밀폐형 또는 개방형 컨테이너에 대한 세부요건
컨테이너를 수직 또는 수평으로 적재할때의 세부요건
컨테이너를 갑판 상부 또는 하부에 적재할때의 세부요건
등에 대해서 물어볼수있습니다.

결과는 아래 형식으로 작성해주세요:
- response: 1 (요청함) 또는 0 (요청안함)
- Why : 컨테이너의 조건을 상세히 요청했기에 세부요건을 원한다고 판단함

예시:
response: 1, why: 밀페형 컨테이너에 품목을 넣는것에 대한 질문임
response: 0, why: 없음

""")

Cont_Opt_detect_prompt = PromptTemplate.from_template("""
당신은 다음 질문 {user_input}에 대해  컨테이너 옵션이 포함되어있는지를 판단하는 전문가입니다.
당신의 지식은 컨테이너 옵션의 판정만으로 제한됩니다

The container options are judged against three, as follows
If no option is given, select "ALL".
If you didn't take any container conditions, return "ALL".
segregation_filter가 주어지지 않아도 "ALL", filter_type가 주어지지 않아도 "ALL", "deck_position"이 주어지지 않아도 "ALL"로 반환한다.
filter_type : "All", "Vertical(수직)", "Horizontal(수평)"
deck_position : "All", "onDeck(갑판 상부)", "underDeck(갑판 하부)"

closed = 밀폐형, open = 개방형 
두가지를 탐색후 4가지 조건중 하나를 골라야합니다
segregation_filter : "All", "closedToClosed", "closedToOpen", "openToOpen"
closedToClosed = 밀폐형 밀폐형
closedToOpen = 밀폐형 개방형
openToOpen = 개방형 개방형


결과는 아래 형식으로 작성해주세요:
ex1)
segregation_filter = 'All'
filter_type = 'All'
deck_position = 'All'
                                                      
ex2)
segregation_filter = 'All'
filter_type = 'All'
deck_position = 'onDeck'                                                    

ex3)
segregation_filter = 'closedToClosed'
filter_type = 'All'
deck_position = 'onDeck'

ex4) 
segregation_filter = 'closedToOpen'
filter_type = 'Vertical'
deck_position = 'underDeck'


""")

final_prompt = PromptTemplate.from_template("""
당신은 다음 질문 {user_input}에 대해 답변을 해야 합니다.

다음 content 만을 활용해서 답변해주세요:

1. Segregation Method 결과:
   {segre_method_result} 
                                            
                                                                          
2. Container Segregation 결과:
   {Contain_Segre_result}

3. Dangerous Goods 세부 정보:
   {dg_details}


답변은 위 content에 있는 내용을 바탕으로만 진행해야 하며, 'segre_method_num' 가 있다면 각각 답변에 출력해줘.
질문의 내용과 무관하거나 content 외의 답변을 하지 마세요.

## 답변 형식:
### 요약
- 간결하고 명확하게 답변하세요.

### 세부 사항
- Segregation Method number('segre_method_num'. 격리방법으로 표기) 정보가 있다면 각 답변에 무조건 출력하세요.
- Segregation Method result 결과가 있다면 빠짐없이 출력하세요.
- 필요한 경우 Dangerous Goods 정보를 포함하세요.

### 참고
- 제공된 Segregation 정보를 기반으로 답변하세요.
""")