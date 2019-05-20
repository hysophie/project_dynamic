import pandas as pd
import os 
import re
from datetime import datetime
import pickle

os.chdir(r'C:\DATA\L.point2019\data')
os.listdir()

Custom = pd.read_csv(os.listdir()[0])
Master = pd.read_csv(os.listdir()[1])
Product = pd.read_csv(os.listdir()[2])
Search1 = pd.read_csv(os.listdir()[3])   
Search2 = pd.read_csv(os.listdir()[-2])
Session = pd.read_csv(os.listdir()[-1])

#%% data preprocessing
#%% (1)Product -> 3개의 키값에서 2개의 키값으로 agg
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


#%% (2)Session
# SESS_DT을 월, 주, 요일로 변환. 
Session['SESS_DT'] = Session['SESS_DT'].astype(str) # int object is not subsriptable 
Session['SESS_DT'] = list(map(lambda x:x[0:4] +'-'+x[4:6]+'-'+x[6:8],Session['SESS_DT']))
Session['MONTH'] = list(map(lambda x:x[5:7],Session['SESS_DT']))

## 월요일을 기준으로 2018-04-02은  04-02 ~ 04-08에 해당. 
Session['WEEK'] = list(map(lambda x:datetime.strptime(x, '%Y-%m-%d').strftime('%Y-%U-1'),Session['SESS_DT'])) 
Session['WEEK'] = list(map(lambda x:datetime.strptime(x, '%Y-%U-%w').strftime('%Y-%m-%d'),Session['WEEK'])) 

## 0 = 월요일, 6 = 일요일 # 1:33
start = datetime.now()
Session['DAY'] = list(map(lambda x:datetime.strptime(x, '%Y-%m-%d').weekday(),Session['SESS_DT'])) 
end = datetime.now()
print (end - start)    

## 휴일 변수;REST 추가 #  2:29 by 승우.

#%% (3) search1,2 서로 다른 key구조를 모델에 적용가능한 형태로 통일.

# merge를 위해 SESS_DT 형식 동일하게 변경. 
Search2['SESS_DT'] = Search2['SESS_DT'].astype(str) # int object is not subsriptable 
Search2['SESS_DT'] = list(map(lambda x:x[0:4] +'-'+x[4:6]+'-'+x[6:8],Search2['SESS_DT']))

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

#%% (4) merge


raw = pd.merge(Session,Custom, how = 'left', on = ['CLNT_ID']) 
raw = pd.merge(raw,Product_agg, how = 'left', on = ['CLNT_ID']) 
raw = pd.merge(raw,Master, how = 'left', on = ['PD_C']) 
raw = pd.merge(raw,Session, how = 'left', on = ['CLNT_ID','SESS_ID']) 
raw = pd.merge(raw,Search,how = 'left', on = ['CLNT_ID','SESS_ID']) 


with open('raw.pickle', 'wb') as f:
    pickle.dump(raw, f)

