### 딥러닝을 활용한 다이나믹 프라이싱.
#### 온라인 행동 데이터를 통한 재구매 기간 예측을 통해 -

---

#### 주제 및 목표 설정

1. 다이나믹 프라이싱이란?  
- 개별 고객의 특성 및 상황에 따라 **실시간**으로 **개인화** 가격을 도출.
  + [정의 출처](http://blog.naver.com/PostView.nhn?blogId=mosfnet&logNo=221320806418)
  
2. 사용 데이터  
- 사용자 온라인 행동 데이터
- oo마트,oo홈쇼핑,oo쇼핑몰 등 온라인 상에서 고객이 행동한 기록

3. 예측 지표 Y 설정 과정
- 사용 데이터가 실시간이 아님, 실시간 측면 보다 **개인화**에 초점을 맞춤. 
- 구매를 한 경우에만 데이터가 있음.
  - 구매확률 -> 6일 이내 재구매확률 or 재구매기간

4. 분석대상 
- 주 소비층인 20-40대(94%)를 기준으로  

#### 사용 데이터 소개
1. 수집기간 및 수집량
- Session,,Product,Search1,Search2,Master,Custom 총 6개의 data set
- 수집기간: 총 6개월(‘18년 4월 ~ 9월)
- 용량: 1.07GB

2. 용어및 변수 설명 
- Main Key: CLNT_ID, SESS_ID
- 핵심 의 정의 .
- Client:  
> cookie를 기반으로 발급, 동일한 사람이라도 접속매체에 따라 복수의 값을 가질 수 있음.  
> 데이터 상에서 고유한 식별 불가능  
- Session:   
> 사용자가 앱/웹 페이지에서 활동하는 영역.   
> 사이트간 이동, 30분 무응답, 자정이 지날시 세션 종료   
> 각 세션 id에 따라 어떠한 세션인지는 특정 불가능.  
- Hit:   
> Session 내에서 사용자의 최소행동단위.  
> session과 마찬가지로 어떤 행위인지는 식별 불가능하고 총 횟수만 기록.  
> ex) 이벤트 배너 클릭, 장바구니 이동, 상품 더보기 등등   

- 상세 설명,'변수설명.docx' 첨부파일 

3.예시를 통한 설명.

- 승우가 옷을 사기위해 **노트북**을 통해 **서울마트**에 접속했다. 
 > client_id = '가나다' 발급, session_id='ABC' 발급, session_seq = 1
- 서울마트에서 옷을 사지 않고 **우리홈쇼핑**에 접속해서 **옷을 샀다**. 
 > client_id = '가나다' 유지, session_id='DEF' 발급, session_seq = 2 -> **이 경우의 데이터만 남음**
- 다음날 **핸드폰**으로 모자를 사기위해 **스마트쇼핑몰**에 접속했다. 
 > client_id = '다라마' 발급, session_id='XYZ', session_seq = 1

#### 전처리  과정

1. Product
- Main key값에 맞게 데이터 집적
- 구매 총액, 평균, 분산, 상품갯수 등을 생성.
- 상품 구매 품목 패턴은 대분류를 기준으로 one-hot 인코딩, 구매빈도/구매여부 변수를 생성.
> ex) 한 세션에서 여성의류를 산 고객 = (1,0,0,0, ... ,0,0)  
> ex) 한 세션에서 여성의류와 남성의류를 산 고객 = (1,1,0,0, ... ,0,0)  
> ex) 한 세션에서 여성의류 3번 산 고객 = (3,0,0, ... ,0,0)  
  
<details>
  <summary>Click to show code!</summary>

  <pre>
    <code>
# -> 3개의 키값에서 2개의 키값으로 agg

# 구매가격 변수를 str -> int 변환.
product['PD_BUY_AM'] = list(map(lambda x:x.replace(",",""),product['PD_BUY_AM']))
product['PD_BUY_AM'] = product['PD_BUY_AM'].astype(int)

# 구매개수 변수를 str&int -> int로 변환.
product['PD_BUY_CT'] = product['PD_BUY_CT'].astype(str)
product['PD_BUY_CT'] = list(map(lambda x:x.replace(",",""),product['PD_BUY_CT']))
product['PD_BUY_CT'] = product['PD_BUY_CT'].astype(int)

## product에 새로운 열 "TOT_AM" 생성 (PD_BUY_AM는 제품 하나 당 개수이므로, 이를 구매한 제품의 갯수와 곱한 "총 지출 금액"이 "TOT_AM"임)
product["TOT_AM"] = product["PD_BUY_AM"] * product["PD_BUY_CT"]

# CLNT_ID와 SESS_ID가 모두 같은 행들을 "TOT_AM","PD_BUY_CT","PD_BUY_AM"에 대해 합계,평균,표준편차를 구한 것
product_agg = product.groupby(['CLNT_ID', 'SESS_ID'])[['TOT_AM','PD_BUY_CT','PD_BUY_AM']].agg(['sum','mean','std'])
product_agg.columns= list(map(lambda x:x[0]+'_'+x[1],list(product_agg)))

## Product Vector mapping

# ## Phase1.
# #### SESS_ID마다 구매한 상품 쌓아 - 그 대분류 쌓아 - 대분류 구매 패턴 (빈도 / 여부)
# #### 변수 1 : 세션 내 쇼핑 Category 구매 빈도(단순 횟수)
# #### 변수 2 : 세션 내 쇼핑 Category 구매 여부(0,1 binary vec)

product = product.sort_values(by=['CLNT_ID', 'SESS_ID'], axis=0)
master= master.sort_values(by='PD_C',ascending=True)
raw=product.merge(master,on='PD_C',how='inner')

#사전식으로 대분류 배열 정렬 (ㄱ으로 시작하여 ㅎ으로 끝나도록)
clac1_list=list(raw['CLAC1_NM'].unique())
clac1_list.sort()
CLAC1_NM_dict=dict(zip(clac1_list,range(0,37)))

#대분류 한글 -> 배정된 숫자로 변경
raw2=raw.replace({"CLAC1_NM": CLAC1_NM_dict})
temp_series = raw2.groupby(['CLNT_ID', 'SESS_ID'])['CLAC1_NM'].agg(lambda x: list(x))
temp_df=pd.DataFrame(temp_series)

#변수2 위해 만들어 둔 multiindex를 column으로 돌린 temp2_df
temp2_df=temp_df.reset_index()

# ## Phase2. 
# #### SESS_ID로 정렬된 Dataframe을 역행하여 {(CLNT_ID,SESS_ID): 36개의 대분류 구매 빈도 vector}의 Dictionary 생성. 
# #### Vector 형태로 Key를 만든 이유는? Multiindex인 Dataframe.index.values하면 tuple형태로 나와서 mapping 편리하게 하기 위함임

# 이런 식으로 empty vector 제작
vec_frame=np.zeros((1,37))

# #### 변수 1 - 10-15분 소요

# 변수 1 단순 빈도 Vector
n=len(temp_df)-1
prod_count_dict={}

while True:
    vec_frame=np.zeros((1,37))
    if n !=-1:
        for i in temp_df.CLAC1_NM[n]:
            vec_frame[0][i]+=1
        prod_count_dict[temp_df.index.values[n]]=vec_frame
        n=n-1
    elif n ==-1:
        print("Done")
        break

# #### 변수 2 - 10-15분 소요
# 변수 2 0,1의 Binary Vector
n=len(temp_df)-1
prod_bin_dict={}

while True:
    vec_frame=np.zeros((1,37))
    if n !=-1:
        for i in set(temp2_df.CLAC1_NM[n]):
            vec_frame[0][i]+=1
        prod_bin_dict[temp_df.index.values[n]]=vec_frame
        n=n-1
    elif n ==-1:
        print("Done")
        break

    </code>
  </pre>
</details>


2. Search
- Main key값에 맞게 데이터 집적
- 개인이 검색한 검색어의 수 (KWD_CNT)
- 개인의 총 검색량 (SEARH_CNT)
- 검색어의 당일 검색량 (SEARH_TOT)
- 개인의 총 검색량 / 검색어의 당일 검색량 
> ex) SEARH_CNT = 5, KWD_CNT = 2, SEARCH_RATIO = 0.01, SEARCH_TOT = 500 이면, 고객은 한세션에서 2개의 검색어를 가지고 5번 검색을 했고, 두 개의 검색어는 당일 총 500번 검색되었다. 따라서 SERCH_RATIO = 5/500 이 된다.
  
<details>
  <summary>Click to show code!</summary>

  <pre>
    <code>
    
# 서로 다른 key구조를 모델에 적용가능한 형태로 통일.

# merge를 위해 SESS_DT 형식 동일하게 변경. 
search2['SESS_DT'] = pd.to_datetime(search2['SESS_DT'], format = '%Y%m%d')

# 검색량 변수를 str&int -> int로 변환 후 이름 변경.
search2['SEARCH_CNT'] = search2['SEARCH_CNT'].astype(str)
search2['SEARCH_CNT'] = list(map(lambda x:x.replace(",",""), search2['SEARCH_CNT']))
search2['SEARCH_CNT'] =  search2['SEARCH_CNT'].astype(int)
search2.rename(columns={'SEARCH_CNT': 'SEARCH_TOT'}, inplace=True) # Search1과 컬럼명이 동일하지만 의미가 다르므로 이름 변경.

# 전체검색량, 검색 키워드 갯수, 개인검색량, 전체검색량 대비 개인 검색량, 변수 생성.
search = pd.merge(search1,session.loc[:,['CLNT_ID','SESS_ID','SESS_DT']],how = 'left', on = ['CLNT_ID','SESS_ID']) 
search = pd.merge(search,search2.loc[:,['SESS_DT','KWD_NM','SEARCH_TOT']],how = 'left', on = ['KWD_NM','SESS_DT']) 
cnt = search.groupby(['CLNT_ID','SESS_ID']).count()['KWD_NM'] # 순서 유의.
search = search.groupby(['CLNT_ID','SESS_ID']).sum() # 이 부분에서 고유한 키값으로 줄어듬. 
search['KWD_CNT'] = cnt
search['SEARCH_RATIO'] = search.SEARCH_CNT / search.SEARCH_TOT  
    </code>
  </pre>
</details>


3. Session
- 기념일변수
> 어린이날, 지방선거, 어버이날등 기념일을 고려하여 변수 생성  
> 각 기념일 전 시점에서 구매량이 증가는 패턴을 고려  
> ex) 어린이날은 5일전에 가장 많은 구매 패턴이 나타남. 어린이날 5일전 변수를 추가.  
-  SESS_DT를 str-> datetime으로 변경,월,요일,주 등 변수를 추가. 
<details>
  <summary>Click to show code!</summary>

  <pre>
    <code>
# SESS_DT을 datetime 자료형으로 변환.
session['SESS_DT'] = pd.to_datetime(session['SESS_DT'], format = '%Y%m%d')
## 월,주,일 변수 생성. 19 -> 1월 1일 이후 19번째 주 double check  0 = 월요일, 6 = 일요일  double check
session['MONTH'] = list(map(lambda x:x.month,session['SESS_DT'])) 
session['WEEK'] = list(map(lambda x:x.week,session['SESS_DT'])) 
session['DAY'] = list(map(lambda x:x.weekday(),session['SESS_DT'])) 

## 휴일 변수; EDA후 유의미하게 구매패턴이 차이나는 'hot day'를 추가

session['Timestamp'] = 0
session['SESS_DT'] = session['SESS_DT'].astype('str')
session['SESS_DT'] = list(map(lambda x:datetime.strptime(x,'%Y%m%d'), session['SESS_DT']))
session['Timestamp'] = list(map(lambda x:datetime.timestamp(x), session['SESS_DT']))

Sat = pd.date_range(min(session.SESS_DT), max(session.SESS_DT), freq='W-SAT') #Saturday
Sun = pd.date_range(min(session.SESS_DT), max(session.SESS_DT), freq='W-SUN') #Sunday

Sat_Timestamp=list(map(lambda x:datetime.timestamp(x), Sat))
Sun_Timestamp=list(map(lambda x:datetime.timestamp(x), Sun))

Holiday = np.array(['20180505', '20180522', '20180606', '20180815', '20180923', '20180924', '20180925', ])
repic_Holiday = np.array(['20180507', '20180613', '20180926']) #5월7일, 9월26일: 대체 공휴일,6월 13일: 지방선거일
Holiday = np.append(Holiday, repic_Holiday)
Holiday = list(map(lambda x:datetime.strptime(x,'%Y%m%d'), Holiday))

Holiday_Timestamp=list(map(lambda x:datetime.timestamp(x), Holiday))

All_Timestamp = Sat_Timestamp + Sun_Timestamp + Holiday_Timestamp

session.ix[session['Timestamp'].isin(All_Timestamp),'Rest']=1

session['Rest'] = 0 #휴일인 날

weekend_Timestamp = Sat_Timestamp
weekend_Timestamp = list(map(lambda x:datetime.fromtimestamp(x), weekend_Timestamp))

session['five_before'] = 0
session.ix[session['SESS_DT'].isin(list(map(lambda x: x+timedelta(days=-5), weekend_Timestamp))), 'five_before'] = 1

# 어린이날 추가
children_day = np.array(['2018-05-05'])
children_day = list(map(lambda x:datetime.strptime(x,'%Y-%m-%d'), children_day))
children_hotdays = []

children_hotdays.append(list(map(lambda x: x+timedelta(days=-3), children_day))[0])
children_hotdays.append(list(map(lambda x: x+timedelta(days=-4), children_day))[0])
children_hotdays.append(list(map(lambda x: x+timedelta(days=-5), children_day))[0])
children_hotdays.append(list(map(lambda x: x+timedelta(days=-6), children_day))[0])

session['children_hotday'] = 0
session.ix[session['SESS_DT'].isin(children_hotdays),'children_hotday'] = 1

# 스승의 날 추가
teacher_day = np.array(['2018-05-15'])
teacher_day = list(map(lambda x:datetime.strptime(x,'%Y-%m-%d'), teacher_day))
teacher_hotdays = []

teacher_hotdays.append(list(map(lambda x: x+timedelta(days=-1), teacher_day))[0])

session['teacher_hotday'] = 0
session.ix[session['SESS_DT'].isin(teacher_hotdays), 'teacher_hotday'] = 1

# 선거일 추가
election_day = np.array(['2018-06-13']) 
election_day = list(map(lambda x:datetime.strptime(x,'%Y-%m-%d'), election_day))

election_hotdays = []

election_hotdays.append(list(map(lambda x: x+timedelta(days=-2), election_day))[0])
election_hotdays.append(list(map(lambda x: x+timedelta(days=-3), election_day))[0])

session['election_hotday'] = 0
session.ix[session['SESS_DT'].isin(election_hotdays), 'election_hotday'] = 1

# Multi Index로 바꾸어 merge 위해 hotday dataframe으로 정리해둠
hotday=session.set_index(['CLNT_ID', 'SESS_ID'])

del(hotday['DVC_CTG_NM'])
del(hotday['ZON_NM'])
del(hotday['CITY_NM'])
del(hotday['Timestamp'])
del(hotday['Rest'])
del(hotday['SESS_DT'])

hotday.sort_index(inplace=True,ascending=True)
    </code>
  </pre>
</details>

4. y labeling
- 날짜간의 차이를 구하고
- CLNT_ID가 변하는 경우에만 none으로 수정
- y를 한칸씩 값을 올려서 학습될 y값과 x들의 row를 동일하게 맞춤. 
<details>
  <summary>Click to show code!</summary>
  <pre>
    <code>
## y labeling
# 날짜 차이 구하기
session = session.sort_values(['CLNT_ID','SESS_DT']) # diff를 사용하기 위해 날짜순으로 정렬
session['DT_DIFF'] = session['SESS_DT'].diff() # (1) 일단은 전체에 대해 차이를 구해준 다음
session.loc[session.CLNT_ID != session.CLNT_ID.shift(),'DT_DIFF'] = None #(2) CLNT_ID가 변하는 경우에만 None로 수정
# 새롭게 라벨 제작
Y = session['DT_DIFF'].dt.days.tolist() # date 형태를 int 형태로 변형
a = list()
a.append(np.nan)
Y = Y[1:]+a # 한칸씩 올리고 마지막에 np.nan 추가 
session['y']=Y # 라벨 추가
session = session[pd.notnull(session['y])] # 라벨값이 np.nan인경우
del raw['DT_DIFF'] # it was just once used to make response variable.
    </code>
  </pre>
</details>
4. NA 처리
- 고객의 성별과 나이는 회원가입을 하지 않은 경우, 생기기  새로운 범주를 만들어서 더미변수화
- search 데이터의 nan는 검색을 하지 않고 구매를 한 경우, 0으로 변경
- 상기 처리 후 na의 비율이 0.01이어서 제외.

#### 추후 과제
1. 딥러닝 모델링
2. 클라우드 사용 
3. 예측 지표를 활용한 다이나믹 프라이싱 전략 고안 

#### 참고
연속형 변수만 사용해서, xgboost로 예측한 결과: 0.63 ㅠㅠ
> xgb.XGBClassifier(max_depth=3, n_estimators=300, learning_rate=0.05  

1로만 예측 결과: 0.53  
0으로만 예측 결과:0.47  
동전 던지기:0.5 ㅎㅎ..  
<details>
  <summary>python으로 구현한 동전던지기 모델이 궁금하다면 클릭!!</summary>
  <pre>
    <code>
import random
flips = [random.randint(0,1) for r in range(len(predictions))]
    </code>
  </pre>
</details>
