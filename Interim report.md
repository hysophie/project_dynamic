### 사용자 온라인 행동 데이터를 활용한 다이나믹 프라이싱.
#### - 딥러닝을 활용한 개인별 재구매 기간 예측을 통해 -

---

#### 주제 및 목표 설정

1. 다이나믹 프라이싱이란?  
- 개별 고객의 특성 및 상황에 따라 실시간으로 개인맞춤화 가격을 도출.

2. 사용 데이터  
- 사용자 온라인 행동 데이터
- oo마트,oo홈쇼핑,oo쇼핑몰 등 온라인 상에서 고객이 행동한 기록

3. 예측 지표 Y 설정 과정
- 사용 데이터가 실시간이 아님, 실시간 측면 보다 개인맞춤화에 초점을 맞춤. 
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
- client, Session, hit
- 상세 설명,'변수설명.docx' 첨부파일 

#### 전처리 과정
1. Session
- 기념일변수
  - 어린이날, 지방선거, 어버이날등 기념일을 고려하여 변수 생성 
  - 각 기념일 전 시점에서 구매량이 증가는 패턴을 고려
  - ex) 어린이날은 5일전에 가장 많은 구매 패턴이 나타남. 어린이날 5일전 변수를 추가. 
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
2. Product
- Main key값에 맞게 데이터 집적
- 구매 총액, 평균, 분산, 상품갯수 등을 생성.
- 상품 구매 품목 패턴은 대분류를 기준으로 one-hot 인코딩, 구매빈도/구매여부 변수를 생성.
  - ex) 한 세션에서 여성의류를 산 고객 = (1,0,0,0, ... ,0,0)
  - ex) 한 세션에서 여성의류와 남성의류를 산 고객 = (1,1,0,0, ... ,0,0)
  - ex) 한 세션에서 여성의류 3번 산 고객 = (3,0,0, ... ,0,0)
  
3. Search
- Main key값에 맞게 데이터 집적
- 개인이 검색한 검색어의 수 (KWD_CNT)
- 개인의 총 검색량 (SEARH_CNT)
- 검색어의 당일 검색량 (SEARH_TOT)
- 개인의 총 검색량 / 검색어의 당일 검색량 
  - ex) SEARH_CNT = 5, KWD_CNT = 2, SEARCH_RATIO = 0.01, SEARCH_TOT = 500 이면, 고객은 한세션에서 2개의 검색어를 가지고 5번 검색을 했고, 두 개의 검색어는 당일 총 500번 검색되었다. 따라서 SERCH_RATIO = 5/500 이 된다.

4. NA 처리
- 고객의 성별과 나이는 회원가입을 하지 않은 경우, 생기기  새로운 범주를 만들어서 더미변수화
- search 데이터의 nan는 검색을 하지 않고 구매를 한 경우, 0으로 변경
- 상기 처리 후 na의 비율이 0.01이어서 제외.

#### 추후 과제
1. 딥러닝 모델링
2. 클라우드 사용 
3. 예측 지표를 활용한 다이나믹 프라이싱 전략 고안 
