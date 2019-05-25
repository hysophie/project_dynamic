# 0. Settings

import pandas as pd
import os 
import re
import pickle
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from datetime import datetime
import numpy as np

os.chdir(r'C:\DATA\L.point2019\data')
os.listdir()

custom = pd.read_csv(os.listdir()[0])
master = pd.read_csv(os.listdir()[1])
product = pd.read_csv(os.listdir()[2])
search1 = pd.read_csv(os.listdir()[3])   
search2 = pd.read_csv(os.listdir()[-2])
session = pd.read_csv(os.listdir()[-1])

#%% 1. Data preprocessing

#%% (1) Dataset 'Product'

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

#%% (2) Dataset 'Session'

# SESS_DT을 datetime 자료형으로 변환.
session['SESS_DT'] = pd.to_datetime(session['SESS_DT'], format = '%Y%m%d')
## 월,주,일 변수 생성. 19 -> 1월 1일 이후 19번째 주 double check  0 = 월요일, 6 = 일요일  double check
session['MONTH'] = list(map(lambda x:x.month,session['SESS_DT'])) 
session['WEEK'] = list(map(lambda x:x.week,session['SESS_DT'])) 
session['DAY'] = list(map(lambda x:x.weekday(),session['SESS_DT'])) 

## 휴일 변수;REST 추가 

#%% (3) Dataset 'search1','search2'

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

#%% (4) Make y 

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
session['y']=Y #라벨 추가
session = session[pd.notnull(session['y])] # 라벨값이 np.nan인경우

#%% (5) Merge datasets

raw = pd.merge(Session,Custom, how = 'left', on = ['CLNT_ID']) 
raw = pd.merge(raw,Product_agg, how = 'left', on = ['CLNT_ID','SESS_ID']) 
raw = pd.merge(raw,Search,how = 'left', on = ['CLNT_ID','SESS_ID']) 

raw = raw.reindex(columns=sorted(list(raw)))
    
#%% (6) Product Vector mapping

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

# #### To pickles

import pickle
with open('PD_CT_Vec.pickle','wb')as handle:
    pickle.dump(prod_count_dict,handle)

with open('PD_BIN_Vec.pickle','wb')as handle:
    pickle.dump(prod_bin_dict,handle)


# ## Phase3. 
# #### raw dataframe과 연결
raw=raw.set_index(['CLNT_ID', 'SESS_ID'])
raw['PD_CT_Vec'] = raw.index.to_series().map(prod_count_dict)
raw['PD_BIN_Vec'] = raw.index.to_series().map(prod_bin_dict)

# ## One hot Encoding
# 도시명은 163개 Unique 값으로, encoding시 너무 많아져 삭제
del(raw['CITY_NM'])

# 성별(CLNT_GENDER), 사용자 기기(DVC_CTG_NM), 행정구역(ZON_NM)은 encoding
encode_df=pd.get_dummies(raw[['CLNT_GENDER','ZON_NM','DVC_CTG_NM']])

# encode_df를 따로 만들어 기존 raw에 join하는 방식으로 했음
raw=raw.join(encode_df)

# 그 후에 따로 기존 string 변수 컬럼 삭제
del(raw['CLNT_GENDER'])
del(raw['DVC_CTG_NM'])
del(raw['ZON_NM'])

# to pickles
with open('raw.pickle','wb')as handle:
    pickle.dump(raw,handle)

#%% (7) 결측치 및 이상치 처리

#%% (8) Data split 

train_set, test_set = train_test_split(raw, test_size=0.3, random_state=42)

with open('C:/DATA/L.point2019/derivation_data/train_set.pickle', 'wb') as f:
    pickle.dump(train_set, f)
    
with open('C:/DATA/L.point2019/derivation_data/test_set.pickle', 'wb') as f:
    pickle.dump(test_set, f)
