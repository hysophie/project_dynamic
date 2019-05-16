import pandas as pd
import os 
import re
from datetime import datetime
from tqdm import tqdm

os.chdir(r'C:\DATA\L.point2019\data')
os.listdir()

Session = pd.read_csv(os.listdir()[-1])
Pruduct = pd.read_csv(r'C:\DATA\L.point2019\data\Pruduct.csv')
Custom = pd.read_csv(os.listdir()[0])
Master = pd.read_csv(os.listdir()[1])
Search1 = pd.read_csv(os.listdir()[3])
Search2 = pd.read_csv(os.listdir()[4])

#%% data Cleansing & preprocessing

# 브랜드 이름에서 [],() 기호 제거.
Pruduct['PD_BRA_NM'] = list(map(lambda x:re.sub("[[,\](,)\s]", "",x),Pruduct['PD_BRA_NM']))

# 구매가격 변수를 str -> int 변환.
Pruduct['PD_BUY_AM'] = list(map(lambda x:x.replace(",",""),Pruduct['PD_BUY_AM']))
Pruduct['PD_BUY_AM'] = Pruduct['PD_BUY_AM'].astype(int)

# 구매개수 변수를 str&int -> int로 변환.
Pruduct['PD_BUY_CT'] = Pruduct['PD_BUY_CT'].astype(str)
Pruduct['PD_BUY_CT'] = list(map(lambda x:x.replace(",",""),Pruduct['PD_BUY_CT']))
Pruduct['PD_BUY_CT'] = Pruduct['PD_BUY_CT'].astype(int)

# SESS_DT을 월, 주, 요일로 변환. 
Session['SESS_DT'] = Session['SESS_DT'].astype(str) # int object is not subsriptable 
Session['SESS_DT'] = list(map(lambda x:x[0:4] +'-'+x[4:6]+'-'+x[6:8],Session['SESS_DT']))
Session['MONTH'] = list(map(lambda x:x[5:7],Session['SESS_DT']))

## 월요일을 기준으로 2018-04-02은  04-02 ~ 04-08에 해당. 
Session['WEEK'] = list(map(lambda x:datetime.strptime(x, '%Y-%m-%d').strftime('%Y-%U-1'),Session['SESS_DT'])) 
Session['WEEK'] = list(map(lambda x:datetime.strptime(x, '%Y-%U-%w').strftime('%Y-%m-%d'),Session['WEEK'])) 

## 0 = 월요일, 6 = 일요일
Session['DAY'] = list(map(lambda x:datetime.strptime(x, '%Y-%m-%d').weekday(),Session['SESS_DT'])) 

## 휴일 변수;REST 추가
hoilday = ['2018-05-05', '2018-05-22', '2018-06-06', '2018-08-15', '2018-09-23', '2018-09-24', '2018-09-25']

rest = []
for idx, date in tqdm(enumerate(Session.SESS_DT)):
    if date in hoilday or Session.DAY[idx] == 5 or Session.DAY[idx] == 6:
        rest.append(1)
    else:
        rest.append(0)

Session['REST'] = rest
# Search1, Search 2 전처리
# merge를 위해 SESS_DT 형식 동일하게 변경. 
Search2['SESS_DT'] = Search2['SESS_DT'].astype(str) # int object is not subsriptable 
Search2['SESS_DT'] = list(map(lambda x:x[0:4] +'-'+x[4:6]+'-'+x[6:8],Search2['SESS_DT']))

# 검색량 변수를 str&int -> int로 변환 후 이름 변경.
Search2['SEARCH_CNT'] = Search2['SEARCH_CNT'].astype(str)
Search2['SEARCH_CNT'] = list(map(lambda x:x.replace(",",""), Search2['SEARCH_CNT']))
Search2['SEARCH_CNT'] =  Search2['SEARCH_CNT'].astype(int)
Search2.rename(columns={'SEARCH_CNT': 'SEARCH_TOT'}, inplace=True)

# 전체 검색량 대비 개인 검색량  변수 생성.
Search = pd.merge(Search1,Session.loc[:,['CLNT_ID','SESS_ID','SESS_DT']],how = 'left', on = ['CLNT_ID','SESS_ID']) 
Search = pd.merge(Search,Search2.loc[:,['SESS_DT','KWD_NM','SEARCH_TOT']],how = 'left', on = ['KWD_NM','SESS_DT']) 
Search['SEARCH_RATIO'] = Search.SEARCH_CNT / Search.SEARCH_TOT

# merge
raw = pd.merge(Pruduct,Custom, how = 'left', on = ['CLNT_ID']) 
raw = pd.merge(raw,Master, how = 'left', on = ['PD_C']) 
raw = pd.merge(raw,Session, how = 'left', on = ['CLNT_ID','SESS_ID']) 

Pruduct.head()
# 한 세션에서 총 검색량 추가
raw = pd.merge(raw,Search1.groupby(['CLNT_ID','SESS_ID']).sum(), how = 'left', on = ['CLNT_ID','SESS_ID']) 
# 한 세션에서 검색 종류 추가
raw = pd.merge(raw,Search1.groupby(['CLNT_ID','SESS_ID']).count()['KWD_NM'], how = 'left', on = ['CLNT_ID','SESS_ID']) 
# 열 이름 변경 
raw.rename(columns={'SEARCH_CNT': 'SEARCH_TOT_CNT', 'KWD_NM': 'KWD_NUM'}, inplace=True)
# 전체 검색량 대비 개인 검색량  변수 추가.
raw = pd.merge(raw,Search.groupby(['CLNT_ID','SESS_ID']).mean()['SEARCH_RATIO'], how = 'left', on = ['CLNT_ID','SESS_ID']) 

list(raw)
raw.CLAC3_NM
test = raw[raw.CLAC3_NM == '스킨케어세트']
