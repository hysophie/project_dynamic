##### Meeting log & Timeline
---

### 프로젝트 주제 및 데이터 선정. 
#### Overview
- 일시: 4/30 20:00~21:00  
- 작성자: 오동건  
- 참석자: 이현아, 김종찬, 최보경, 류승우, 오동건

#### Contents and Decisions
1. 주제: 온라인 행동 데이터를 활용한 다이나믹 프라이싱.  
- 다이나믹 프라이싱이란?  
: 개별 고객의 특성 및 상황에 따라 **실시간**으로 **개인맞춤화** 가격을 도출.  

  + [정의 출처](http://blog.naver.com/PostView.nhn?blogId=mosfnet&logNo=221320806418)

2. 사용 데이터 
- OO기업의 사용자 로그 데이터 및 검색 데이터

3. 타임라인
- 5/14 (화) – 연사 강연.    
- 5/21 (화) - 데이터 전처리 마무리, 모델링 시작.  
- 6/4 (화) - 1차 완료 예정일.  

#### Forward plans
- 데이터 구조 파악  
- 분석 범위 결정  
- 협업 방식 고민  

---
### 데이터구조 파악 및 분석범위 결정.
#### Overview
- 일시: 5/4 17:00~17:40  
- 작성자: 오동건  
- 참석자: 이현아, 김종찬, 최보경, 류승우, 오동건  

#### pre-shared

<details>
  <summary>Click to expand!</summary>
  
동건: 
1. Dynamic pricing 대상.  
조건(성별,나이,상품군,세션,검색)에 따라 상품을 구매할 가중치를 예측한 뒤, 다이나믹 프라이싱 전략 기획     
ex) 0~1사이의 값을 갖는 가중치를 만든다면, 0.5 근처의 사람들을 dynamic pricing 대상으로! 

2. 분석범위.  
소분류로 분석하면, 데이터가 너무 sparse해지므로 상품군은 중분류까지만 사용했으면 좋겠다. 단 고객범위는 최대한 다양하게

3. 데이터 구조 질문.  
Search1과 Search2의 search_cnt가 서로 다른 의미? 확인했는 데 수치가 서로 다르다.   
Session은 클라이언트의 전체 세션에 대한 정보는 아니고 구매행위가 이루어진 세션에 대한 정보만?  
Seseion dastaset에 포함된 Session의 기준이 무엇?

보경:

1. 분류: Master 데이터셋에 class2(원래 얘기한 중분류)로 분류하면 좋을 듯  
2. 최종 목표: 다이나믹 프라이싱을 위한 개인별 가중치 도출  

하위 지표: 
- 검색 - 많이 검색할수록(frequency)
- 상품 및 상세 페이지 - 많이 방문할수록(frequency)
세션 - 세션간 시간간격이 좁을수록(고려를 여러 번 한다), 세션의 길이가 짧을수록(구매 고민에 시간을 많이 쓰지 않는다)

3. 데이터 구조 질문
TOT_session_HR_V가 어느 단위의 시간이지
Session sequence가 무엇이지

승우:

1. 중요 지표
- Session.csv: TOT_PAG_VIEW_CT,  TOT_SESS_HR_V(애매, 온전히 쇼핑에만 쏟을 가능성?) / DVC_CTG_NM(애매, 기기 특성?)
- Product.csv: HITS_SEQ, PD_BUY_AM, PD_BUY_CT
- Custom.csv: CLNT_GENDER, CLNT_AGE

2. 분류
- 상품범위: CLAC2_NM

3. 의문점:
- 1. Pricing 방향성
   - 많이 산 사람들에게 많은 할인을 해 줄 것인가? / 고민을 많이 한 사람들(지표 ex. 클릭 수)들로 하여금 구매를 유도할 것인가?
   (:방향성3와 관련하여 모델링의 개괄적인 방향성은 확실히 하고 가고 싶다)
- 2. Session.csv의 SESS_SEQ가 정확히 무엇인가? 
   - 예를 들어, CLNT_ID 5874829 동일한 날짜 20180903 세션ID는 늦게 발급 받았음에도 SESS_SEQ가 앞서는 경우가 생김. 
- 3. 성별에 따라 모델링을 달리할 것인가? (Male: 101063, Female: 570616)
- 4. E-Commerce 연령대 선택은 어떻게? (30대가 가장 많고, 2,3,40대에 몰려 있음.)
- 5. 괴상한 행동 양태를 갖고 있는 소비자에 대한 고려? (Pricing에 혜택을 주나?)
   - ex. CLNT_ID 4736937 비슷비슷하고 가격은 똑같은 제품군에 대해 3154번 구매? 4월부터 9월까지? ???

4. 방향성:
- CLNT_ID, SESS_ID 를 Key값으로 Product, Session Data Merging
- Product.csv, Session.csv를 통해 Key값들을 바탕으로 실제 검색 활동이 구매로 이어지고 있는 가에 대한 고찰 
   - (-> 이것에 대한 객관적인 지표도 결정)
- 모델링 시작 이전에, Input, Layer, Output에 대한 개괄적인 방향성은 잡아놓고 시작했으면 좋겠음
- 추후에 동일 상품군에 대한 타사 제품 가격을 이용할 것인지 상의

* 지금 하고 있는 고민들이, NN이 실제로 Dynamic Pricing에 어떻게 활용되는지에 대한 Reference(개괄적 코드)를 찾지 못해
활용 양상을 잘 알지 못하기에 어쩌면 현재 스스로가 불필요한 고민을 하고 있는 것인지도 모른다는 생각. 
모델링에 대한 개괄적인 내용은 꼭 한 번 짚고 넘어갔으면 좋겠음
(현재 수동으로 고려하고 있는 내용들이 모델 내 weight에서 자동으로 고려된다면 몇 가지 불필요한 고민을 하고 있다고 생각 됨)*

</details>

#### Contents and Decisions
1. 데이터 구조
- 변수 설명서를 확인하고 함께 논의. 

2. 분석 범위
- 상품 분석으로 중분류까지 사용
- e-commerce 구매력에 대한 통계 자료를 통해, 핵심고객층을 선정. 20~40대를 대상으로 분석.   
  - (E-commerce 고객통계.pdf 참고)

3. 협업 방식
- 전처리단계: 데이터셋을 나눠서 전처리 방식을 고민
- 모델단계: 동일한 테스트/트레이닝 셋에 대해서 개별적으로 모델 만들고 최종적으로 . 

#### Forward plans

1. 데이터 구조 숙지, 질문 사항 공유
2. 다이나믹 프라이싱을 어떻게 할지 ML모델 outline 그려오기 또는 레퍼런스 찾아서 요약하기.



---

###  다이나믹 프라이싱 Outline 
#### Overview
- 일시: 5/7 19:30~21:00  
- 작성자: 오동건, 이현아
- 참석자: 이현아, 김종찬, 최보경, 류승우, 오동건  
#### pre-shared

<details>
  <summary>Click to expand!</summary>
	
동건  
- 특정 시점의 데이터만 존재하기 때문에, 실시간 프라이싱은 불가능
- 단, 데이터 집적단위가 개인이기 때문에 개인맞춤화는 가능

제안1  
- 사용자 행동에 대한 데모데이터 만든 후 구매확률 예측
1. 현재 데이터는 구매를 한 사람들의 온라인 행동 데이터만 존재.
2. 구매를 안 한 사람들의 온라인 행동의 분포를 유추하여 데모데이터를 만듬
3. 구매 여부에 따라 0,1 라벨을 만들고 지도학습 모델 생성
4. 0~1사이의 가중치를 예측하여 사용자 온라인 행동에 따른 가격차별화!
-  데모데이터의 비율을 어떻게 할 것인가에 대한 레퍼런스 필요! 즉 고객전환율!!
	
제안2
- 데이터에서 새롭게 지불용의 y를 정의하고 이를 예측
1. 지불용의에 대한 세부 정의는 데이터 탐색 단계에서 결정
2. 상품 구매 소요시간, 구매빈도, 구매량 등으로 y를 정의할 수 있을 듯? 
3. 단 구매를 한 사람들만 있기 때문에, 데이터는 모두 지불용의가 상품의 가격보다 높은 상태. 
-  다이나믹 프라이싱을 하는 데 한계가 될 수 있음

승우
- 초/분 단위로 업데이트 되는 진정한 의미의 Real Time Data가 아니기에 결국 개별 Customizing 문제

제안
- 사용자들의 소비 행태에 대한 새로운 지표를 만든다.\
*단순한 하나의 시나리오*
- 1. ex. PD_BUY_AM*PD_BUY_CT ~ TOT_PAG_VIEW_CT + TOT_SESS_HR_V + CLNT_GENDER + CLNT_AGE (+다른 변수들) MSE를 Minimize 하도록 가중치 학습(Client별 적용, Cookie 기록량이 적은 사람들은 제외)      
- 2. Softmax -> 새로운 prediction variable로 확률값 생성
- 3. 확률값의 분포를 보고, 특정 확률값에 따라 소비자군 분리(Segmentation) -> 소비자군 별로 다른 할인폭 적용 등의 Strategy

- 문제는, 
  - 1. 높은 할인폭을 적용 받은 사람들이 가격이 낮아졌다고 해서 구매를 늘릴지는 또 생각해봐야 할 문제.
   필요 이상으로 살 것 같지는 않고, 또 그렇다고 다른 상품군으로 넘어갈까에 대해서도 의문이 듦.
  - 2. 개별 Customizing이 아니라 Clustering의 의미가 짙어 보이는데, 이것을 Dynamic Pricing으로 볼 수 있겠는가. 

종찬

제안1
- 구매하지 않은 세션과 구매한 세션간의 패턴 분석을 통한 구매 확률 예측 (동건님과 유사)
1. Session 데이터 중에서 구매하지 않은 세션과 구매한 세션을 구분 ( 0, 1 )
 - 구매한 session 데이터가 구매하지 않은 session 데이터에 비해 작기 때문에 imbalance 문제 해결
2. 머신러닝을 통해 패턴을 찾고 특정 session에 따라 구매 확률 예측 ( 0 ~ 1 )
 - 유의미한 feature 추가필요 (날짜 -> 요일 등) / 구매하지 않은 session데이터의 경우 현재로서는 feature가 약간 부족해보임
3. 구매확률이 높은 session 중에 가격이 높아져도 구매 가능성이 높은 session 구분 
  - 반대로 구매확률이 조금 낮지만 가격을 낮췄을 때 소비가 높아질 session 패턴 분석은 demand function을 모르면 총 이익에 도움이 되는지 알기 어려우니 패스 / 또한 구매확률이 높은 사람에게 가격을 낮춘다는 건 (거의) 무쓸모 이므로 패스!  
 - 가격을 수정하는 A/B test를 통해서 실제 효과를 볼 순 없지만 가설이나 인덱스를 설정해서 끝까지 해보는 데 의미가 있을 듯 
 - 이 인덱스에 대해서 좀 더 논의가 필요할 듯 ( 예를 들어 동일상품이 다른 사이트 보다 높은 가격임에도 불구하고 산 경우를 찾아서 지도 학습 )
 
현아
 
1)	수요와 공급을 활용한 Dynamic pricing
-	공급 데이터는 우리에게 없음
-	수요를 추정하기: SNS에서의 날짜 별 언급량 + 사이트에서의 검색량의 변화량 (Search2 활용)
-	그 상품/상품군의 수요가 올라가면(그 상품/상품군이 trendy해지면), 그 상품의 가격을 올리기

2)	구매할 확률 예측해서 Dynamic Pricing
-	구매확률 예측에 활용될 변수: 검색 횟수(search1) / 그 세션의 total page view, total session hr v / 과거 구매금액 / 과거 구매횟수 / 고객의 특성(성별, 나이 등)
-	구매하지 않을 것 같은 사람에게는 가격을 내려주고, 구매할 것 같은 사람에게는 가격을 올리기
-	어떤 고객이 어떤 물건을 구매할지 예측
-	Q) 이미 특정 고객이 특정 상품에 대해 몇 번 검색을 해본 상태에서 가격을 내리면, 그 사람이 그 물건을 사려고 할까? (오히려 더 떨어질 것을 기대하는 게 아닐까?)

3)	추가적으로 고려할 점
-	상품군 별로 나누어 분석을 진행해야 할까?
-	가격을 얼마나 올리고 내려야 할까?  다른 쇼핑몰의 가격도 쉽게 알 수 있으므로, 가격을 올리면 다른 쇼핑몰로 가버리는 게 아닐까? (e-commerce에서 dynamic pricing이 효과 있으려면 어떻게 해야 할까?)


보경
1) 다이나믹 프라이싱을 강화학습 관점에서 접근
Dynamic pricing on e-commerce platform with deep reinforcement learning
 논문 리뷰: https://hoondongkim.blogspot.com/2018/10/reinforcement-learning-e-commerce.html?fbclid=IwAR21M3ktj5GLWMuC3Ta1qCtau77VrCYa_xde8f4gWGgIrbsL3mMQNRib1yc
 
2) 상품군을 타입별로 분류 Fast moving customer goods(FMCGs) / Luxury 

제안 
</details>

#### Contents and Decisions

1. 분석 방법
- pruduct는 구매를 한 세션만 존재하는 반면, session에는 pruduct 세션도 존재한다. 이를 구매를 안한 경우로 가정하고 모델을 만듦
- 단, 우선적으로는 비율을 확인해야하고 사용. 비율이 너무 적으면 데모데이터를 만들거나 붓스트랩 샘플을 만드는 방향으로! 
- 데모데이터는 현재데이터 셋에서 근거를 찾아 최대한 합리적으로! 

2. 이상데이터 제거
- 세션의 날짜와 시퀸스가 일치하지 않거나 비상적인 소비패턴을 보이는 데이터는 제거. 
- 이상치 기준 논의 필요.

3. a/b 테스트의 가능성? 
- 모델을 만든 다음에, 가설을 세워서  a/b 테스트를 진행하고 실제 마케팅 효과를 검증 -> 모델 진행 후 추후 논의. 

4. 상품을 특성별로 나누기
- (ex) 사치재 vs. 보통재
- 같은 상품의 price level 별 revenue를 그래프로 그린 논문 참고할 수도.

5. 그 외
- feature 브레인스토밍 (ex) 검색한 후 샀는지 아닌지를 0, 1로 표현 / 전체 검색량 대비 개인의 검색량
- 다른 쇼핑몰의 가격을 크롤링 하는 방안도 추후에 고려.

6. 모두의 딥러닝의 단체수강.
- 회의전에 간단하게 내용 공유하기.

#### Forward plans

1. 피쳐 모델링.
2. a/b 테스트 고민해보기.

---

###  Feature modeling & Preprocessing (1)

#### pre-shared

<details>
  <summary>Click to expand!</summary>

동건:  
1. 재구매여부 y 제안
- 데이터를 재확인한 결과, 모든 세션은 구매를 한 경우만 존재.구매를 안 한 세션에 대한 데모데이터를 만드는 방향에 대한 환기 필요.
- 다만, 데모데이터를 만들지 않고 **'재구매여부'** 를 y로 사용할 수 도 있을 듯. 특정 세션이 후 며칠 이내에 재구매를 했으면 1값을 주고 하지 않았으면 0값을 주는 방향으로, 이런 접근은 지금의 데이터로 충분히 만들 수 있고, 변수 설명도 의미를 가짐. (의미 있는 EDA의 가능성.)

2. feature modeling
- Session, Pruduct 데이터를 중심으로 전처리와 변수 추가.(code uploaded), Search1,2는 논의 할 부분이 있기 때문에 idea를 우선 제시  
- Session
  - SESS_DT 변수를 활용해, 구매가 이루어진 시점의 월, 주, 요일 변수 추가.
  - 추후 휴일여부, 주말여부, 계절도 포함을 시킬 지 논의.
- Pruduct
  - 구매가격, 구매량 변수가 ,가 포함된 str 자료형이여서 ,를 제거하고 int로 변환.
  - 브랜드 이름에 [],()이 들어가 동일한 브랜드임에도 다르게 인식 -> [],()을 제거.
- Search1,Search2
  - 두 데이터셋은 구매를 하지 않은 경우에도 자료 포함. 
    - 데모데이터를 만든다면 비율을 어떻게 설정할지에 대한 근거로 활용 가능(특히 Session1)
    > 재확인 결과, 구매를 하지 않은 경우에 자료가 포함된 것이 아니라, 여러검색어를 사용해서 행이 늘어난 경우 였음! 고유한 키 값으로는 오히려 전체 세션보다 작은 값이 나옴. 즉, 검색을 안하고 구매한 사람에 대한 정보와 검색을 하고 구매한 사람의 정보만 있음!
  - 전체검색량 대비 개인검색량을 개인적 관심의 측도로 사용.
  - 전체검색량의 추세를 변수로 사용. ex) 회귀직선의 기울기
  - 그 외에도 search1, search2는 변수들 간의 조합을 통해 유의미한 변수를 찾을 수 있을 것으로 예상 
  > 검색어 데이터 활용 사례 조사해도 좋을 듯? 
		
- 우선은 Pruduct, Session, Master를 병합해서 5백만\*24 dataframe을 생성
  - 분석 방향을 구체적으로 결정한 이후, Search1을 Search2 데이터를 어떻게 넣을 지 고민 필요. 
  
  종찬 : 
  1. 구매량/검색량 혹은 머무는 시간 y 제안
  - 전략 : 가격을 잘 비교하지 않는 꼼꼼하지 않은 유저(호구)를 구별하여 가격을 높인다.
  - 검색을 많이 하면서도/머무는 시간이 많으면서도 구매량이 낮은 경우 비호구일 가능성이 높다는 가정  
  - 따라서 y가 낮을 수록 비호구일 가능성이 높다고 가정
  - 이러한 호구 및 비호구들의 Session 패턴학습
  
보경:
- pruduct 데이터 중심 이해와 전처리(pruduct_type. csv & product 분류별 평균 가격 & COUNT.ipynb 추후 업로드)
- 대분류 37가지, 중분류 128가지
- 평균 가격 높은 중분류: DIY 가구 > 냉장고 > 세탁기 > 컴퓨터 > TV
- 평균 가격 낮은 중분류: 속옷/양말 < 필기도구 < 닭고기류
- (직관적이나) 중분류의 평균 가격이 낮을 수록 / 구매 횟수가 많음을 확인하였음. 
하지만! '닭고기'의 경우 평균 가격이 6위로 낮지만 구매 횟수가 하위 18위 -> 롯데 계열사 온라인 채널로 굳이 축산물 및 소비재를 사려하지 않는가?
주로 의류, 패션, 가구 등의 상품목으로 구성되어 있음
- offline retail stores에 대한 product category 분류 모델은 논문들에서 많으나, e-commerce product category 분류 모델은 찾아보지 못했음.

현아:

	Feature 후보
-	우리의 딥러닝 모델: 온라인 행동 데이터들을 input feature로 주고, 이 사람이 구매 여부의 label을 0,1로 줘서 학습시킴 -> output: 각 사용자의 해당 세션의 구매확률 예측
1)	Session
-	구매한 세션의 간격 (CLNT_ID별로, 직전 SESS_SEQ와의 gap)
-	세션 접속한 device (DVC_CTG)
2)	Pruduct
-	특정 고객의 구매 상품의 다양성(상품 가짓수, 카테고리 개수) -> 그 사람이 모든 종류의 제품을 이 쇼핑몰에서 사고 있는지, 특정 제품or제품군만을 그 쇼핑몰에서 사고 있는지
3)	Master
-	구매한 제품의 중분류

	Idea 제안
1)	y label 제안 -> 구매한 고객 중에서도 충성고객(1) / 그냥고객(0)으로 label 붙이기
-	충성고객: 구매금액x구매횟수가 일정 수준 이상인 고객
-	그냥고객: 구매금액x구매횟수가 일정 수준 이하인 고객
-	충성고객vs.그냥고객의 온라인 활동 패턴 학습 후, 특 정 고객이 충성고객이 될 가능성 예측
2)	비지도학습도 시도해보는 건 어떨까?
-	구매한 고객들 중에서도, Clustering을 통해 여러 cluster로 고객군 분류 -> cluster 별 구매금액/온라인 행동의 차이가 있는지

	A/B test 고민해보기
-	https://www.business-science.io/business/2019/03/11/ab-testing-machine-learning.html

	그 외 읽은 참고자료
-	https://towardsdatascience.com/an-overview-of-categorical-input-handling-for-neural-networks-c172ba552dee -> Handling categorical input for NN (one-hot encoding을 기본적으로 사용하지만, 다른 방법도 많음!
-	https://www.upwork.com/hiring/for-clients/log-analytics-deep-learning-machine-learning/

승우:

- y label: '재구매'여부 제안
  - 세션을 왔다갔다 하기만 하고 구입하지 않는 사람
   : 실제로 구입하는 고객들에게 가격 인하의 focus를 맞추어야 한다고 생각
   : 현재 train data도 결국에는 물품을 구매한 적이 있는 사람들의 데이터이기 때문에, 
     이 데이터를 갖고 구매하지 않은 고객들의 predict를 행하는 것은 무리가 있어 보임. 
     > 결국 focus는 실제로 구매한 사람들의 데이터를 바탕으로 각종 feature들로 그들의 행동 양태를 예측하고 
       집단군 별로 할인폭을 결정하는 방향으로 나아가야 한다고 생각. 
     
   : 문제는 과연 얼마를 주기로 물건을 구입하는 사람들에 focus를 맞출 것인가?
     일주일에 한 번, 한 달에 한 번, 두 달에 한 번 구입하는 사람들에 대한 할인의 적용은 분명 달라야 한다고 생각.
     자주 구입하는 사람들일수록 할인을 해주면 오히려 더 많은 수량을 구입할 가능성이 높기에? 

</details>

#### study contents

<details>
  <summary>Click to expand!</summary>

동건:
- 서울대학교 etl 공개강좌에서 CNNs 수강.
- convolution(합성곱)의 직관적 의미
- CNN의 5가지 layer (input,cov'n,activate,pooling,fully-connected)
- Convolution lasyer의 3가지 필수 hyperparameter (filter depth, stride, zero-padding)
- CNN praticatl tips 
  - C-R-C-R-P이 한 set로 해서 여러 set를 이어서 네크워트를 구성
  - input layer: 픽셀 크기가 2^n를 갖는 정사각형으로 가공해야 pooling이 수월
  - convolution layer: 3\*3, 5\*5 와 같은 작은 홀수를 필터 크기로 사용. pad = 1, stride = 1
  - pooling layer = 2\*2, stride = 2, maxpooling

승우:
- GAN model 공부 
- GAN: Generative Adversarial Network.
  - Generator와 Discriminator가 서로 속고 속이는 경쟁을 함.
  - Generator는 가능한한 Real Data와 유사한 Fake Data를 만드려, Discriminator는 가능한한 Fake Data와 Real Data를 잘 구분해내려.
  - 'Network'라는 단어가 말해주는 것처럼, 신경망 알고리즘을 기반을 하고 있음. 
  - Backpropagation을 통해 가중치를 조절해나가며, Generator가 현실과 가장 유사한 데이터를 내어놓으려고 노력함.
  - '비지도학습'의 NN으로의 적용으로, 상당히 Hot한 분야.
  - Generator의 성능을 기준으로 GAN model의 성능 평가
 > 구매자 데이터가 부족하다면 GAN 모델을 통해 실제 구매 데이터와 유사한 행동 양상을 보이는 Fake Data를 만들어낼 수 있을 것. 
 > 구매하지 않은 사람의 데이터를 GAN을 통해 얻어낸다는 것은 잘못된 것. -> 구매하지 않은 사람에 대한 고려는 다른 방식으로 이루어져야.
 > Neural Network 기반이기에 현재 우리가 향하고 있는 방향성과 잘 맞아 보이나, 다만, 모델의 이해나 적용이 결코 쉽지는 않아 보임. 
  
- 모두를 위한 딥러닝 Lab 1-4, 8
   - 텐서 overview
   - Dimension, Shape, Rank, Axis, Matmul, tf.reduce_mean, tf.reduce_sum, argmax, reshape(squeeze, expand), one hot, casting, stack

보경:
 - 모두를 한 딥러닝 RL 시즌 Lecture 1-3
 - RL 기본: Agent가 전체 Environment의 각 State에서 Action을 하고 Rewards를 얻는다.
 - Q-function
 	1) 개념: '내가 해봐서 아는데, 어떤 State에서 각 Action을 취하면? 이런 Reward(Quality, 즉 Q)를 주더라' 라고 알려주는 형님
	2) Q-function의 가정
	- S'에서는 Q를 안다고 가정한다.
	- I am in s. When I do action a, I'll go to s'. When I do action a, I'll get reward r.
	- Q in s', Q(S',a')이것은 이미 알고 있다고 가정 들어감(그 다음 state에서의 리워드를 안다고 가정하고 현 state에서의 리워즈 추정)
	3) 공식화
	- Q(s,a) = r+maxQ(s',a') <- r은 rewards	
- Dummy Q-learning algorithm
	>절차 
	1) 각 s(state), a(action), 에서 Q hat(s,a)를 0으로 input
	2) 현 s를 살핀다. 
	3) 다음을 무한 반복한다.
		Action a를 고르고 실행한다
		당장의 reward r을 받는다
		다음 state s'을 살핀다
		Q hat(s,a) <- r(받은 reward) + maxQ(s',a')
		S에서 s'로 넘어간다.

현아:
- 모두를 위한 딥러닝 Lab10, ConvNet의 conV 레이어 만들기
- Lab 10 : NN for MNIST (relu 활용) -> Xavier initialization (weight 초기화) -> Dropout layer 넣기 (network이 깊어지면 overfitting의 문제가 생기는데, 이를 해결하기 위해 network 일부를 끊음) * Dropout 시에 주의할 점: train 할 때는 keep_prob(network의 몇%를 keep할 것인가)를 0.5~0.7 정도로, test 할때는 무조건 "1"
- 다양한 종류의 optimizer : 일반적으로 ADAM optimizer를 많이 씀 (성능이 가장 좋아서) => tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

</details>

#### Overview
- 일시: 2019.05.11 17:00~18:00
- 작성자: 최보경
- 참석자: 최보경, 오동건, 이현아, 류승우

#### Contents and Decisions

1. 우리의 Dynamic pricing의 방향은?  
이미 살 사람이 지불할 가격을 변동시키는 것 << 살지 말지 고민하는 사람을 가격 변동을 통해 구매를 유도하는 것
(Revenue 측면, 도덕 측면, 긍정적인 측면, 사업성 측면)
Purchase behavior based segmentation(전통적)
구매를 많이 하는 사람(할인을 해주는 것은 미래의 revenue를 그저 앞으로 당겨오는 것) / 구매를 한번도 한 적이 없는 사람 / 구매를 한-두번 한(재구매율이 낮은) 사람
-> 어느 소비자를 프라이싱 변동을 통해 Revenue를 끌어 올리는게 좋을까? '구매를 한-두번 한 사람'으로 좁힌다.

2. y값은? '재구매율'  
재구매율이 DP를 할 수 있는 완벽한 Key는 아니지만, 하나의 기준이 될 수 있다.
검색만 하고 구매 안 한 애들(400만 가량)을 걸러내고, 집단 검색한 애들 중에서 구매한 애들만 KEEP하여 고려(500만 가량)
구매를 안 한 애들에 대한 세션이 없어서 -> 검색 O, 구매 X는 버린다.

3. 재구매율 패턴을 어떻게 잡을 것인가?  
-> 누가 5일 이내에 구매를 했는가 yes 1, no 0. 즉 101010101와 같은 binary type 후 mean으로 계산하여 가중치화

4. 개인별 purchase 주기는?  
-> 논문 기반으로 e-commerce에서 참고

5. 데이터가 6개월 어치인 한계  
-> 한계 보완 필요. 향후 논의

#### Forward plans

1. 상품분류를 전부 활용하여 모델링? (1) 변수에 넣을 것인가? (2) 상품 분류를 유의미할 분류만 활용해서 각 모델을 만들 것인가? 
EX. 중분류/ 대분류/ 또 다른 기준(가격이 높고 낮고/ 구매횟수 많고 적고/ 소비재고 luxury냐 등
2. 변수 생각, 데이터를 더 세밀히 보자.

---

###  Feature modeling & Preprocessing (2)

#### pre-shared

<details>
  <summary>Click to expand!</summary>

동건:
- Search1,2 데이터 전처리한
  -  한 세션에서 개인이 사용한 검색어의 종류의 수 -> KWD_CNT
  - *검색어의 종류와 상관없이*  한 세션에서 개인의 총 검색량  -> SEARCH_CNT
  - *검색어의 종류와 상관없이*  한 세션에서 검색어의 당일 전체 검색량 -> SEARCH_TOT 
  - *검색어의 종류와 상관없이*  개인의 총 검색량 / 검색어의 당일 전체 검색량 -> SEARCH_RATIO
  - EX) SEARH_CNT = 5, KWD_CNT = 2, SEARCH_RATIO = 0.01 이면, 고객은 한세션에서 2개의 검색어를 가지고 5번 검색을 했고, 두 개의 검색어는 당일 총 500번 검색되었다. 따라서 SERCH_RATIO = 5/500 이 된다.   


승우:

  Act1
  - 6개의 File, 각종 전처리
  - Session데이터:
    - Session 데이터에 Rest 변수를 새로 만들어, 휴일 물품 구입시 1, 그렇지 않을시 0을 labeling.
      (휴일: 토요일 + 일요일 + 국정 공휴일 between April and September)

  Act2
   - 휴일과 구매활동 간의 관계 조사 

   - 총 건수: 5024906 (구매한 사람들에만 한정한 데이터)
   - 휴일 당일 구매: 1447120건, 425715명의 고객
   - 휴일 하루 전 구매: 1308817건, 407180명의 고객
   - 휴일 이틀 전 구매: 1436076건, 439858명의 고객
   - 휴일 사흘 전 구매: 1563313건, 469269명의 고객
   - 휴일 나흘 전 구매: 1614446건, 479673명의 고객
   - 휴일 5일 전 구매: 1746188건, 503364명의 고객
    > 휴일에서 멀어질수록, 나흘, 5일 전의 구매활동이 더 왕성한 경향이 있다.

   - 6일전, 7일전은 결국 그 전 주 주말과 겹치기에 큰 의미를 두기 어려울 것 같다는 생각. 
     > 추후에, 평상적인 주말과 국가지정 공휴일 간의 차이도 살펴보도록 하겠음. 
   - 당연히 건수로는 평상적인 주말이 훨씬 많을 것이기에, 각각 주말의 수, 공휴일의 수를 기준으로 비율을 봐야할 것

</details>

#### study contents
<details>
  <summary>Click to expand!</summary>
승우:

- 모두를 위한 딥러닝 Lab 5-10 수강.



</details>

#### Overview

일시: 5.18 10:30~12:20  
작성자: 오동건  
참석자: 최보경, 이현아, 김종찬, 류승우, 오동건  
지각: 류승우  

#### Contents and Decisions

0. 코드리뷰

1. 재구매고객의 구매텀의 분포  

- right shewed 된 분포.
> 0,1의 비율을 비슷하게 나눌 수 있는 구매 텀을 정하는 것도 좋은 방법일듯. 
- 총 구매가격으로 인해 구매텀 차이가 나지 않는다. 
> 상품에 따라 y를 나누지 않아도 될 듯? 
 
이상치 발견: 한 세션에 1억을 산 사람.

2. 클러스터링을 통한 EDA

- 숫자변수들로만 진행중
- 중분류로 묶어서 클러스터링

3. 휴일변수 

- 휴일 4,5일에 구매가 증가하는 경향이 있다. 이를 활용한 변수를 생성.


#### Forward plans

1. 승우: 휴일 4일전, 5일전 변수 만들기.  NA value 기준 찾고 채우기
2. 동건: 7일 단위 구매텀 정의 test,train set 나누기. 
3. 보경: product data set 전처리.
4. 종찬: product data set 전처리.
- 상품코드-> 대분류로 , 구매가격 평균, 구매가격 분산, 구매상품 갯수, 등등 집적하면서 새로운 변수 만들기.
- 세션 내 구매 상품 가격 평균
- 세션 내 구매 상품 가격 분산
- 상품 몇개 -> 세션별 상품 구매 개수
- 상품코드 -> 대분류 쌓아서 -> 대분류 구매 패턴 (어렵겠다)
- 대분류가 혼합되면 1, 혼합 안되면 0 : 대분류 혼합 여부
> 대분류가 혼합되면 1~36까지의 숫자를 할당하면 될 것 같아요! 대분류가 36개 니깐..
5. 현아: 구매텀 결정. 7일에 맞는 레퍼런스 찾기. & 이상치 제거 

---

###  Feature modeling & Preprocessing (3)

#### pre-shared

<details>
  <summary>Click to expand!</summary>

동건:  
- 재구매율을 1,0으로 나누지 않고 처음부터 재구매기간을 예측하거나 아니면 multinomial classification을 재고  
- test/train 나눌 때, (1) 완전 무작위 (2) 월을 기준으로 (3) 고객을 기준으로  
> 개인적으로는 월을 기준으로 나누는게 raw data의 squencial한 측면을 잘 살릴 수 있지 않을까 생각되는데, 논의 필요.
- Session의 DT_DIFF 생성과정에서 논리적 오류 의심.
> 2018.03.01에 사고 2018.03.09에 재구매했다면, 03.01에 8 days가 들어가야함. 지금은 3.09에 들어가 있음
- 0days 처리 어떻게 할 지 논의 필요.
- 남은 전처리: Y /변수추가(휴일,상품범주)/이상치 및 사용하지 않을 컬럼 제거/NA처리/더미변수화  
- 모든 구성원의 git bash 사용 및 code 및 csv 파일 중간 정리. 

승우:
- EDA tactic 변경
  - 이전에는 토,일 요일을 한 번에 고려해 당일~5일 전을 고려 했음.
  - 그런데, 일요일은 토요일의 바로 다음날이기에 둘을 동시에 고려해버리면, 하루 전의 건수를 count할 경우, 토요일에 대한 정보가 중복돼 버림
     -> 자료 왜곡
  - 따라서, 토요일'만'을 기준으로 잡아 당일~6일 전으로 구매 건수를 counting 한다면 토요일부터 그 전주 일요일까지 모든 요일을 고려할 수 있게 됨
     -> 2018년에는 5월 5일, 5월 22일, 6월 6틸, 8월 15일, 9월 23일, 9월 24일, 9월 25일의 공휴일이 있는데, 
        특히나 어린이날은 토요일이고 추석 연휴는 토요일과 밀접하게 연관되어 있기 때문에 이 두 날은 제외하고 counting
	(cf. 5월7일, 9월26일:  대체 공휴일, 6.13일:지방선거일)
	
   -result:
     - 총 구매 건 수: 5024906
     - 토요일 구매 건 수: 525898, 개별 구매자 수: 197304
     - 금요일 구매 건 수: 562808, 개별 구매자 수: 214649
     - 목요일 구매 건 수: 632533, 개별 구매자 수: 236395
     - 수요일 구매 건 수: 665858, 개별 구매자 수: 247887
     - 화요일 구매 건 수: 674328, 개별 구매자 수: 248199
     - 월요일 구매 건 수: 783059, 개별 구매자 수: 275952
     - 일요일 구매 건 수: 652031, 개별 구매자 수: 231609
 
      - 이전에 월, 화의 값들에 1을 주기로 했다면, tactic 변경 후에는 월요일의 값들에 1을 주겠다. 

     * 토요일 구매 건 수 들의 평균을 기준으로 판단해보건대, 
     - 어린이날: 어린이날의 3~6일 전 구매 많음
     - 현충일: 산발적으로 많은 날들이 좀 있음.. (빼야되나 말아야되나)
     - 지방선거: 지방선거 2~3일 전 구매가 좀 많음
     -  (부처님오신날, 광복절은 비슷비슷)
       ->  어린이날, (현충일), 지방선거:기준일 대비 구매 시점으로 새로이 각각의 변수로 줄 가능성 (1, 0)
    - 근데 이상하게 추석 연휴 일주일 전까지는 보통의 토요일보다도 구매 건 수가 압도적으로 낮다 (???)
       -> 내 생각에는 추석의 경우에는 일반적인 e-commerce 상거래를 이용해서 소위 말로 '찍어내는' 물품이 아니라
          좀 더 specialized된 물품을 생산하는 (전문적인 한우 판매 장소?) 그런 곳들에서 정성들인 선물을 하지 않을까 하는데..
	  -> 이 부분이 좀 의아함..

    - + 스승의 날: (휴일은 아니지만) -> 하루 전 구매가 압도적으로 많다?
          (어린이 날은 집으로 배달하기에 미리 구매해놓고, 집 안에 놔둘 가능성?)
	  (스승의 날은 과일/ 꽃구매 같은 것들이 많으니, 선생님 댁으로 하루 전에 배달할 가능성?)
	  
	  > tactic 변경 이후의 기준대로라면, SAT-5, 즉 월요일인 날짜들에 '1'을 부여하게 될 것. 
	  > 특별한 날들의 적용 여부 논의 필요. (어린이날, 현충일, 지방선거와 관련해서도 변수를 만들 것인지, 만든다면 각각의 기준일에 대하여 며칠까지로 잡을 것인지 상의 필요해보임.)
	  
 - 결측치(NA) 처리? 
   * 결측치 처리의 GUIDE LINE
   > 결측 데이터의 종류 파악 -> 결측값 유형 탐색 -> 결측치의 원인 및 각각의 원인에 따른 처리 방법 결정
   
    * 결측값의 종류 파악
     1. 완전무작위결측: 어떤 변수의 결측값이 다른 변수와 관련이 없을 때
     2. 무작위결측: 어떤 변수의 결측값이 다른 변수와 연관되어 있지만, 그 변수의 결과와는 관계가 없는 경우
        EX. 남자: 우울증 관련 진단에 응답률이 낮지만, 이것이 우울증 정도와 관련이 있는 것은 아니다.
     3. 비무작위결측: 완전무작위결측, 무작위결측이 아닌 경우. 
        EX. 소득이 적은 사람이 소득에 대한 결측값을 가지기가 쉬워 (저소득자들은 자신의 소득을 기입하지 않으려는 경향이 있기 때문에)
	
     * 결측값 유형 탐색
      1. 표를 그려본다. (어떤 변수에 NA값이 몰려있는가?)
      2. 결측치 끼리의 상관관계가 있는가? (Correlation with Missing Values)
      
     * 결측치의 원인 파악 및 원인에 따른 처리 방법 결정
      1. 합리적 접근법: 변수들 간의 관계를 이용해서 결측값을 채워 넣는다.   
      2. 완전 제거법: 결측치가 있는 행 자체를 지워버린다.
         -> 불가: 데이터 반 이상이 지워짐.
      3. 다중 대체법: 하나의 observation에 2개 이상의 결측치가 존재할 때. (가장 어려운 대체 방법)

         * 결측치를 avg, median, mode 등으로 단순 대체하는 방법은 최대한 쓰지 말 것을 강조. Bias가 커지고, 변수들간 관계 왜곡. 
	    -> 모델링의 결과에 악영향.
	    - sklearn.preprocessing Imputer에 쉽게 이 값들로 impute할 수 있는 패키지가 있기는 함  
	
       - 데이터 결측치 분포
         - 'CLNT_AGE', 'CLNT_GENDER', 'KWD_CNT', 'PD_BUY_AM_std', 'PD_BUY_CT_std', 'SEARCH_CNT', 'SEARCH_RATIO', 'SEARCH_TOT',   
	   'TOT_AM_std', 'TOT_PAG_VIEW_CT', 'TOT_SESS_HR_V' 변수에 결측치가 존재
	 - 7개 변수에서 결측치 비율이 0.5를 넘음.  (4개, 3개씩 짝을 지어 결측치 비율이 각각 완전히 같음)
	   -> 현재 같고 있는 데이터 셋이 전처리 완료된 데이터 셋이 아니기에, 추후에 전처리 한 후에 다시금 처리해야 함.
	 - 히트맵 그려보면, NA Value 존재가 상관관계를 갖고 있는 경우들이 보인다. -> 역시 데이터 전처리 조금 더 세분화 해야 함. 
        
	* 제언 -> ㄴ)
	  - 결측치가 이렇게나 많고, 각 변수가 계속 늘어나고, 특히 대분류에 대한 dummy들까지 들어오면,
	    -> 합리적 접근법이나  다중 대체법이 굉장히 어려워질 것 같다는 생각.
	    * 동일한 CLIENT에 다양한 Session이 있다면 continuous한 값들에 대해서는 변수별로 observation 들의 평균을 내면 어떨까?
	      -> 만약 해당 Session들 다수에 해당 변수에 대해 결측값이 많다면, 비슷한 feature를 가진 CLIENT들의 분포를 참고해서 결측값을 채운다. 
	    * 성별과 같은 Discrete한 변수
	      -> 단순히 남녀 비율에 맞춰 임의로 MALE, FEMALE을 부여한다는 것은 조금 어불성설 같음.
	      -> 그렇다고 MALE->1, FEMALE->2, 그리고 제 3의 성에 3을 부여한다는 것 자체도 이상
	      -> 그렇다면 대분류를 보고(1~36) 대분류가 남성용품, 여성용품 중 어느 것일까를 판단하고 Male, Female 처리하는 것은 어떨까
	         - 남자가 여자에게 선물, 여자가 남자에게 선물 이런 경우는 어쨌든 이성의 기호를 반영하는 것이기에 그대로 갖고가도 된다고 생각
		 - 대분류로 분류하기 애매할 경우에는.. 애매하네.  (KCI_FI001583868.pdf -> 논문인데 파이썬에서 구현할 수 있을까?)
		 
현아:

1) 재구매 term 결정
- "6일"로 결정 (6일을 기준으로 나누었을 때 0과 1 각 label에 배정되는 데이터의 갯수가 가장 유사함)
- Reference: 인터넷 쇼핑 행태 리포트에 따르면, 인터넷 쇼핑몰 사용자들은 평균적으로 "5.08일"에 한 번씩 쇼핑함. (https://www.digieco.co.kr/KTFront/board/board_view.action?board_id=issue_trend&sort_order=&kind=&list_page=2&list_gubun=title&list_gubun2=&searchtext=&board_seq=12059&etc1=387&etc2=#)

2) 이상치 제거 기준
- "한 고객의 한 세션에서의 총 구매금액"의 상위 3%를 이상치로 간주
- Reference: 인터넷 쇼핑몰에서의 1회 평균 구매금액은 7.2만원(PC), 6.0만원(모바일) => 위의 reference와 같은 출처
- 상위 3% 제거 시, 1회 평균 구매금액은 74,515원 / 1회 구매금액의 최댓값은 397,940원(상식 수준에서 받아들일 수 있는 금액임)
   
   
보경:


맡은 부분: SESS_ID마다 구매한 상품들을 Stack - 그 상품들의 대분류(CLAC1_NM)를 Stack -> 대분류 구매 패턴 추출
> File: preprocessing_accumulation_Bonnie.ipynb / PD_CT_Vec.pickle / PD_BIN_Vec.pickle

구매 패턴 추출에 있어서, 어떻게 상품구매 rows들을 담아냈는가? 
>	- 36가지 대분류를 사전식 정렬(ㄱ-ㅎ) 후 0~36의 숫자에 할당
>	- 36 shape의 Vector(python상으로는 ndarray)의 Empty Frame을 만든 후
>	- 두 가지 type의 변수를 만들었음.
>	1) Session 내 구매한 대분류의 '빈도'(단순 횟수): 변수 이름은 PD_CT_Vec
>	2) Session 내 구매한 대분류 '여부' (0,1의 Binary vector): 변수 이름은 PD_BIN_Vec

문제점 발생
>	- 다른 Client ID 이나 같은 Session ID 개수가 2만개 가량 발생.
>	- 일단은 코드 내에 중복되는 Session ID를 리스트로 뽑아 냈음 (redundant_key의 리스트에 담아둠, 향후 활용)
>	- 즉, 일단은 최초 마주치는 Session ID의 구매 패턴만 딕셔너리에 저장하고 나머지 같은 Session ID는 skip and append to list
>	- Henry의 데이터프레임과 연결할 때에는 Dictionary mapping 활용하여서 -> 다른 client들인데 같은 구매 패턴 벡터가 변수로 들어가게 됨.
>	- Henry 변수들에 NaN이 많은데 무슨 일일까?
	
이 문제를 향후 어떻게 해결할까?
>	- 해결 방안1 : SESS_ID 겹치는 2만개 가량의 Records를 제거한다 -> 데이터 손실, 쉬움
>	- 해결 방안2 : SESS_ID 이름을 바꿔서 전부 다시 진행한다 -> 정확, 시간 소요
 
 </details>

#### study contents
<details>
  <summary>Click to expand!</summary>

</details>

#### Overview
- 일시: 05.21 19:30~22:00
- 작성자: 이현아  
- 참석자: 최보경, 류승우, 김종찬, 오동건, 이현아

#### Contents and Decisions

1) 재구매 간격 label
> - 시간A와 시간B 사이의 재구매 간격에 대한 label은 시간A에 붙여주어야 함
> - 재구매 term을 continuous하게 예측하기 (개인 맞춤 dynamic pricing)!! 재구매 여부를 0,1로 예측하는 것(X) 
> 	- 이렇게 재구매 term을 예측했을 때의 단점: 학습 데이터가 편향되어 있는 문제

2) Train/Test dataset을 어떻게 나눌까?
> - 무작위로 나누기!
>	- sequential하게 분석할 수는 없음
>	- k-fold cross validation 시도해볼 수 있음
>	- 4,5,6,7,8,9 각 월 별로 균형을 맞춰서 train/test set을 나눌 수 있는 방법?
>	- 휴일, 일, 월 다 넣어서 모델 만들기

3) CLNT_ID 관련 이슈
> - CLNT_ID는 같은데, SESS_ID는 다른 경우가 있음
> 	- CLNT_ID, SESS_ID 값을 multi-index로 하기
> - CLNT_ID 변수 아예 빼버리기 / 각 CLNT_ID 별로 모델을 따로 만들기 ...

3) 그외 세부 결정사항
> - 0 days를 label에 포함시키기
> - SESS_SEQ의 차이를 변수로 만들어보기 (시간 남으면)
> - 성별 NA는 3으로 놓고 dummy 변수로 만들기
> - 한 session에 구매한 금액의 standard deviation은 NaN이 너무 많으니까 빼기

4) 역할 분담
> - 종찬: y label 위로 올려주는 작업 (시간A 이후에 시간B에 재구매를 했다면, 시간A로 y label 옮겨주기)
> - 승우: NA 처리 / holiday 변수 수정
> - 동건: 전처리
> - 보경: 변수들 one-hot encoding / Product vector 변수 수정 
> - 현아: 이상치 제거 (0,1로 만들어놓기)

#### Forward plans

- 이번주 금요일 자정: Raw data 전처리 완료
- 이번주 토요일: 모여 모델링 Start
- 6/1 토요일: 1차 발표, 그 전까지 보경 모델링 
- 6/4 ~ 8일 주: 보경 모델링 선행
- 6/18 ~ 22일 주: 동건, 승우, 현아, 종찬 모델링 스퍼트 내기
- 6/22일 ~ 25일: PPT 준비 & 완성
---

###  Feature modeling & Preprocessing (4)

#### pre-shared
<details>
  <summary>Click to expand!</summary>

승우:
 * 변수설명
   - Rest: 휴일 -> 1
   - five_before: 토요일 -5일 -> 1 (평일 국가 공휴일은 제외)
   - children_hotday: 어린이날 -3~-6일 -> 1
   - teacher_hotday: 스승의날 -1일 -> 1
   - election_hotday: 지방선거일 -2~-3일 -> 1
 
 * NA value 채우기
   - 채워야 할 변수: 'CLNT_AGE', 'CLNT_GENDER', 'KWD_CNT', 'SEARCH_CNT', 'SEARCH_RATIO', 'SEARCH_TOT', 'TOT_PAG_VIEW_CT', 'TOT_SESS_HR_V'
 
   - 두 가지 방향에서 고민 중
     - 1. CLNT_AGE, CLNT_GENDER 변수가 중요
       - CLNT_AGE의 결측치는 곧 CLNT_GENDER의 결측치 -> 비회원 구매 (비율 약 12%) 
       - 각 observation이 두 변수 모두가 비어있기 때문에 상관관계가 거의 없는 다른 변수들을 고 이들을 예측하는 것은 bias가 너무 커질 것
       - '약 13% observation 날리고, 나머지 87% 데이터로 진행하는 것은 어떨까'라는 1안
     
     - 2. softmax를 써서 CLNT_AGE군 예측을 해보려고 함.
       - 2-(1) 괜찮은 연속형 설명 변수 두 개('PD_BUY_AM_mean', 'PD_BUY_CT_mean')로 성능 테스트  
         - 성능: 약 0.4129
       - 2-(2) 'TOT_PAG_VIEW_CT', 'TOT_SESS_HR_V' 결측치가 0.01%도 안돼 
       - 얘네 결측치 지우고 4개의 설명 변수 ('PD_BUY_AM_mean', 'PD_BUY_CT_mean', 'TOT_PAG_VIEW_CT', 'TOT_SESS_HR_V')
         - 성능: 약 .4199

     - 따라서, CLNT_AGE 결측치 행 지우거나 말거나인데, 각각의 장단점이 있다.
     
    - 어차피 'TOT_PAG_VIEW_CT', 'TOT_SESS_HR_V'는 결측치 비율이 많지 않아서 나중에 해당 observation은 지워도 상관x
    - 나머지 변수들의 NA 비율은 50%가 넘는데? 중요한 정보인 건 맞는데 너무 심해서.. 
	
 
  
 보경:
 * Product vector 변수 (CLNT_ID, SESS_ID)의 고유한 tuple로 모든 벡터 유지하였음 
 * One-hot Encoding
   -  string 형태의 변수는 현재 4가지
   -  도시명(CITY_NM),성별(CLNT_GENDER), 사용자 기기(DVC_CTG_NM), 행정구역(ZON_NM)
   -  각 163개, 3개, 3개, 16개의 Unique 값을 지님
   -  도시명은 변수가 너무 많아져 삭제 - 성별, 사용자기기, 행정구역 One-hot encoding으로 변수 유지 => 총합 48개 가량 column의 raw data가 됨
 * preprocessing_Demian.py 항목들 수정하였음
   -  의문점: Product dataset 전처리 부분에 벡터 만드는 세세한 코드도 넣나요? 아님 pickle로 간단히?
 
</details>

#### study contents
<details>
  <summary>Click to expand!</summary>

승우: 
 * 모두를 위한 딥러닝 
   - Lecture Lab11 CNN '이론' 재수강
   - Lecture Lab11 CNN, Lab12 RNN 12-1 ~ 12-4 (Dynamic RNN, Time Series RNN 남음) 

</details>

#### Overview
- 일시: 05.25 14:00~17:00
- 작성자: 이현아  
- 참석자: 최보경, 류승우, 김종찬, 오동건, 이현아

#### Contents and Decisions

1) 전처리 진행상황 공유
> - 보경 
	- CLAC1_NM (상품 대분류 0~36)
> 	- PD_CT_Vec (상품 대분류 구매 빈도 벡터)
> 	- PD_Bin_Vec (상품 대분류 구매 여부 binary 벡터)
> - 승우
> 	- 어린이날 / 스승의 날 / 지방선거 3개의 holiday 선정
> 	- (ex) 어린이날 - 3일~6일 전이 구매가 많은 것을 관찰. 3일~6일 전의 날짜들에 “1”을 넣음.

2) 결측치 채우기
> 0으로 결측치 채우기 (SEARCH_CNT 등)

3) Age 변수
> 20대, 30대, 40대(전체 데이터의 94% 차지)의 데이터만 사용하기

4) 마지막 구매("DT_DIFF"가 NaN인 row들) 모아서 따로 dataset으로 만들기
> - 이 NaN을 나중에 우리 모델로 채워넣는 것도 좋은 아이디어!

5) 이상치 제거는 각자 주관에 맞게 하기

#### Forward plans

- 5.25(토) : 전처리 완료
- 5.25(토) ~ : 각자 모델링
- 6/1(토) : 1차 발표(동건), 그 전까지 보경 모델링 
- 6/4 ~ 8일 주: 보경 모델링 선행
- 6/18 ~ 22일 주: 동건, 승우, 현아, 종찬 모델링 스퍼트 내기
- 6/22일 ~ 25일: PPT 준비 & 완성

---

###  Modeling

#### Overview
- 일시: 06.22 14:00~16:00
- 작성자: 이현아  
- 참석자: 최보경, 류승우, 오동건, 이현아

#### Contents and Decisions

1) 각자 모델링
> - 변수도 알아서 선정
> - 데이터의 범위도 알아서 선정 (ex. 특정 상품군만 선택할지, 전체 데이터를 대상으로 할지)
> - 어떤 모델로 할지 (ex. 회귀, 분류 등)

2) 상품군 선정 
> - (방법1) 가장 많이 구매된 상품부터
> - (방법2) 가격이 낮은 상품부터

3) 4개의 평가 기준
> - 사용한 변수 갯수 & raw data 개수
> - 예측한 N의 갯수
> - 걸린 시간
> - 컴퓨터 사양
> - 정확도 (regression이면 R-squared, classification은 Accuracy로 하기)

#### Forward plans

- 6.25(화) GH 오기 전까지: 모델링
- 6.26(수) 각자 모델 비교 & ppt 만들기
