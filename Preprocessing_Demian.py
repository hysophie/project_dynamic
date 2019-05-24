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

Custom = pd.read_csv(os.listdir()[0])
Master = pd.read_csv(os.listdir()[1])
Product = pd.read_csv(os.listdir()[2])
Search1 = pd.read_csv(os.listdir()[3])   
Search2 = pd.read_csv(os.listdir()[-2])
Session = pd.read_csv(os.listdir()[-1])

#%% 1. Data preprocessing

#%% (1) Dataset 'Product'

# -> 3개의 키값에서 2개의 키값으로 agg
# 브랜드 이름에서 [],() 기호 제거.
Product['PD_BRA_NM'] = list(map(lambda x:re.sub("[[,\](,)\s]", "",x),Product['PD_BRA_NM']))

# 구매가격 변수를 str -> int 변환.
Product['PD_BUY_AM'] = list(map(lambda x:x.replace(",",""),Product['PD_BUY_AM']))
Product['PD_BUY_AM'] = Product['PD_BUY_AM'].astype(int)

# 구매개수 변수를 str&int -> int로 변환.
Product['PD_BUY_CT'] = Product['PD_BUY_CT'].astype(str)
Product['PD_BUY_CT'] = list(map(lambda x:x.replace(",",""),Product['PD_BUY_CT']))
Product['PD_BUY_CT'] = Product['PD_BUY_CT'].astype(int)

## product에 새로운 열 "TOT_AM" 생성 (PD_BUY_AM는 제품 하나 당 개수이므로, 이를 구매한 제품의 갯수와 곱한 "총 지출 금액"이 "TOT_AM"임)
Product["TOT_AM"] = Product["PD_BUY_AM"] * Product["PD_BUY_CT"]

# CLNT_ID와 SESS_ID가 모두 같은 행들을 "TOT_AM","PD_BUY_CT","PD_BUY_AM"에 대해 합계,평균,표준편차를 구한 것
Product_agg = Product.groupby(['CLNT_ID', 'SESS_ID'])[['TOT_AM','PD_BUY_CT','PD_BUY_AM']].agg(['sum','mean','std'])
Product_agg.columns= list(map(lambda x:x[0]+'_'+x[1],list(Product_agg)))

# SESS_ID별 구매한 상품 대분류 패턴 파악 - 향후 Mapping (Bonnie 수정 예정)
Product = pd.merge(Product,Master, how = 'left', on = 'PD_C')
CLAC1_NM_dict=dict((c, i) for i, c in enumerate(sorted(Product['CLAC1_NM'].unique())))
Product = Product.replace({"CLAC1_NM": CLAC1_NM_dict}) #대분류 한글 -> 배정된 숫자로 변경

#%% (2) Dataset 'Session'

# SESS_DT을 datetime 자료형으로 변환.
Session['SESS_DT'] = pd.to_datetime(Session['SESS_DT'], format = '%Y%m%d')
## 월,주,일 변수 생성. 19 -> 1월 1일 이후 19번째 주 double check  0 = 월요일, 6 = 일요일  double check
Session['MONTH'] = list(map(lambda x:x.month,Session['SESS_DT'])) 
Session['WEEK'] = list(map(lambda x:x.week,Session['SESS_DT'])) 
Session['DAY'] = list(map(lambda x:x.weekday(),Session['SESS_DT'])) 

## 휴일 변수;REST 추가 

#%% (3) Dataset 'search1','search2'
# 서로 다른 key구조를 모델에 적용가능한 형태로 통일.

# merge를 위해 SESS_DT 형식 동일하게 변경. 
Search2['SESS_DT'] = pd.to_datetime(Search2['SESS_DT'], format = '%Y%m%d')

# 검색량 변수를 str&int -> int로 변환 후 이름 변경.
Search2['SEARCH_CNT'] = Search2['SEARCH_CNT'].astype(str)
Search2['SEARCH_CNT'] = list(map(lambda x:x.replace(",",""), Search2['SEARCH_CNT']))
Search2['SEARCH_CNT'] =  Search2['SEARCH_CNT'].astype(int)
Search2.rename(columns={'SEARCH_CNT': 'SEARCH_TOT'}, inplace=True) # Search1과 컬럼명이 동일하지만 의미가 다르므로 이름 변경.

# 전체검색량, 검색 키워드 갯수, 개인검색량, 전체검색량 대비 개인 검색량, 변수 생성.
Search = pd.merge(Search1,Session.loc[:,['CLNT_ID','SESS_ID','SESS_DT']],how = 'left', on = ['CLNT_ID','SESS_ID']) 
Search = pd.merge(Search,Search2.loc[:,['SESS_DT','KWD_NM','SEARCH_TOT']],how = 'left', on = ['KWD_NM','SESS_DT']) 
cnt = Search.groupby(['CLNT_ID','SESS_ID']).count()['KWD_NM'] # 순서 유의.
Search = Search.groupby(['CLNT_ID','SESS_ID']).sum() # 이 부분에서 고유한 키값으로 줄어듬. 
Search['KWD_CNT'] = cnt
Search['SEARCH_RATIO'] = Search.SEARCH_CNT / Search.SEARCH_TOT  

with open('C:/DATA/L.point2019/derivation_data/Search.pickle','wb') as f:
    pickle.dump(Search,f)

#%% (4) Make y 

Session = Session.sort_values(['CLNT_ID','SESS_DT']) # diff를 사용하기 위해 날짜순으로 정렬
Session['DT_DIFF'] = Session['SESS_DT'].diff() # (1) 일단은 전체에 대해 차이를 구해준 다음
Session = Session.loc[Session.CLNT_ID == Session.CLNT_ID.shift()]# (2) ID가 바뀌는 시점은 재구매기간을 특정할 수 없으므로 삭제.

days7 = Session.DT_DIFF[677236]

Y = []
for i in tqdm(Session.DT_DIFF):
    if i <= days7:
        Y.append(1)
    else:
        Y.append(0)

Session['y'] = Y

#%% (5) Merge datasets

raw = pd.merge(Session,Custom, how = 'left', on = ['CLNT_ID']) 
raw = pd.merge(raw,Product_agg, how = 'left', on = ['CLNT_ID','SESS_ID']) 
raw = pd.merge(raw,Search,how = 'left', on = ['CLNT_ID','SESS_ID']) 

raw = raw.reindex(columns=sorted(list(raw)))

with open('C:/DATA/L.point2019/derivation_data/raw.pickle', 'wb') as f:
    pickle.dump(raw, f)
    
#%% (6) Product Vector mapping
    
# multi Index로 바꾸어 raw2
raw=raw.set_index(['CLNT_ID', 'SESS_ID'])

# product 구매 패턴 vector를 mapping
with open('PD_CT_Vec.pickle','rb') as vec:
    prod_count_dict=pickle.load(vec)
with open('PD_BIN_Vec.pickle','rb') as vec:
    prod_bin_dict=pickle.load(vec)

raw['PD_CT_Vec'] = raw.index.to_series().map(prod_count_dict)
raw['PD_BIN_Vec'] = raw.index.to_series().map(prod_bin_dict)

#%% (7) 결측치 처리


#%% (8) One-hot encoding

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

with open('raw.pickle','wb')as handle:
    pickle.dump(raw,handle)
    
#%% (9) Data split 

train_set, test_set = train_test_split(raw, test_size=0.3, random_state=42)

with open('C:/DATA/L.point2019/derivation_data/train_set.pickle', 'wb') as f:
    pickle.dump(train_set, f)
    
with open('C:/DATA/L.point2019/derivation_data/test_set.pickle', 'wb') as f:
    pickle.dump(test_set, f)
