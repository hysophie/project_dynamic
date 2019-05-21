#!/usr/bin/env python
# coding: utf-8

# ### Settings

# In[1]:


import pandas as pd
import os
import matplotlib.pyplot as plt
import re
import numpy as np
from datetime import datetime
import time


# In[2]:


os.chdir(r'C:\Users\BokyungChoi\Desktop\GrowthHackers\project_dynamic\dataset')

product = pd.read_csv('pruduct.csv', encoding='utf-8')
session = pd.read_csv('Session.csv', encoding='utf-8')
search1 = pd.read_csv('Search1.csv', encoding='utf-8')
search2 = pd.read_csv('Search2.csv', encoding='utf-8')
custom =  pd.read_csv('custom.csv', encoding='utf-8')
master =  pd.read_csv('Master.csv', encoding='utf-8')


# In[3]:


# 브랜드 변수에서 특수문자 제거
product['PD_BRA_NM'] = list(map(lambda x:re.sub("[[,\](,)\s]", "", x), product['PD_BRA_NM']))

# 구매가격 변수를 str -> int 변환.
product['PD_BUY_AM'] = list(map(lambda x:x.replace(",",""),product['PD_BUY_AM']))
product['PD_BUY_AM'] = product['PD_BUY_AM'].astype(int)

# 구매개수 변수를 str&int -> int로 변환.
product['PD_BUY_CT'] = product['PD_BUY_CT'].astype(str)
product['PD_BUY_CT'] = list(map(lambda x:x.replace(",",""),product['PD_BUY_CT']))
product['PD_BUY_CT'] = product['PD_BUY_CT'].astype(int)

# product를 CLNT_ID 순으로 정렬
product = product.sort_values(by=['CLNT_ID'], axis=0)

## product에 새로운 열 "TOT_AM" 생성 (PD_BUY_AM는 제품 하나 당 개수이므로, 이를 구매한 제품의 갯수와 곱한 "총 지출 금액"이 "TOT_AM"임)
product["TOT_AM"] = product["PD_BUY_AM"] * product["PD_BUY_CT"]


# In[4]:


session = session.sort_values(by=['CLNT_ID', 'SESS_ID'], axis=0)
product = product.sort_values(by=['CLNT_ID', 'SESS_ID'], axis=0)


# In[5]:


raw1 = pd.merge(session, product, how='left', on = ['CLNT_ID', 'SESS_ID'])


# ### Henry codes

# In[6]:


# '세션 내 구매 상품 가격' 단순 합계 & 평균 & 표준편차

# tot_buy_am: CLNT_ID와 SESS_ID가 모두 같은 행들을 "TOT_AM"에 대해 합계를 구한 것
tot_buy_am = product.groupby(['CLNT_ID', 'SESS_ID'])['TOT_AM'].agg('sum').tolist()

# mean_buy_am: CLNT_ID와 SESS_ID가 모두 같은 행들을 "TOT_AM"에 대해 평균를 구한 것
mean_buy_am = product.groupby(['CLNT_ID', 'SESS_ID'])['TOT_AM'].agg('mean').tolist()

# std_buy_am: CLNT_ID와 SESS_ID가 모두 같은 행들을 "TOT_AM"에 대해 표준편차를 구한 것
std_buy_am = product.groupby(['CLNT_ID', 'SESS_ID'])['TOT_AM'].agg('std').tolist()


# In[7]:


# '세션 내 상품 구매 개수' 단순 합계 & 평균 & 표준편차

# tot_buy_ct: CLNT_ID와 SESS_ID가 모두 같은 행들을 "PD_BUY_CT"에 대해 총합를 구한 것
tot_buy_ct = product.groupby(['CLNT_ID', 'SESS_ID'])['PD_BUY_CT'].agg('sum').tolist()

# mean_buy_ct: CLNT_ID와 SESS_ID가 모두 같은 행들을 "PD_BUY_CT"에 대해 평균를 구한 것
mean_buy_ct = product.groupby(['CLNT_ID', 'SESS_ID'])['PD_BUY_CT'].agg('mean').tolist()

# std_buy_ct: CLNT_ID와 SESS_ID가 모두 같은 행들을 "PD_BUY_CT"에 대해 표준편차를 구한 것
std_buy_ct = product.groupby(['CLNT_ID', 'SESS_ID'])['PD_BUY_CT'].agg('std').tolist()


# In[8]:


# '세션 내 구매한 상품의 가격' 단순 총합 & 평균 & 표준편차

# tot_prod_price: CLNT_ID와 SESS_ID가 모두 같은 행들을 "PD_BUY_AM"에 대해 총합를 구한 것
tot_prod_price = product.groupby(['CLNT_ID', 'SESS_ID'])['PD_BUY_AM'].agg('sum').tolist()

# mean_prod_price: CLNT_ID와 SESS_ID가 모두 같은 행들을 "PD_BUY_AM"에 대해 평균를 구한 것
mean_prod_price = product.groupby(['CLNT_ID', 'SESS_ID'])['PD_BUY_AM'].agg('mean').tolist()

# std_prod_price: CLNT_ID와 SESS_ID가 모두 같은 행들을 "PD_BUY_AM"에 대해 표준편차를 구한 것
std_prod_price = product.groupby(['CLNT_ID', 'SESS_ID'])['PD_BUY_AM'].agg('std').tolist()


# In[9]:


session["TOT_BUY_AM"] = tot_buy_am
session["MEAN_BUY_AM"] = mean_buy_am
session["STD_BUY_AM"] = std_buy_am
session["TOT_BUY_CT"] = tot_buy_ct
session["MEAN_BUY_CT"] = mean_buy_ct
session["STD_BUY_CT"] = std_buy_ct
session["TOT_PROD_PRICE"] = tot_prod_price
session["TOT_PROD_PRICE"] = mean_prod_price
session["TOT_PROD_PRICE"] = std_prod_price


# #### -> Why so many NaNs?

# ### Bonnie codes
# #### SESS_ID마다 구매한 상품 쌓아 - 그 대분류 쌓아 - 대분류 구매 패턴 (빈도 / 여부)
# #### 변수 1 : 세션 내 쇼핑 Category 구매 빈도(단순 횟수)
# #### 변수 2 : 세션 내 쇼핑 Category 구매 여부(0,1 binary vec)

# In[11]:


product = product.sort_values(by=['CLNT_ID', 'SESS_ID'], axis=0)
master= master.sort_values(by='PD_C',ascending=True)


# In[12]:


raw2=product.merge(master,on='PD_C',how='inner')
raw2.head()


# In[13]:


#사전식으로 대분류 배열 정렬 (ㄱ으로 시작하여 ㅎ으로 끝나도록)
clac1_list=list(raw2['CLAC1_NM'].unique())
clac1_list.sort()
clac1_list[0:3]


# In[14]:


CLAC1_NM_dict=dict(zip(clac1_list,range(0,37)))
CLAC1_NM_dict


# In[15]:


#대분류 한글 -> 배정된 숫자로 변경
raw3=raw2.replace({"CLAC1_NM": CLAC1_NM_dict})


# #### Phase1. Stacking 구매 상품 - 15분 소요

# In[16]:


# temp_series = raw3.groupby(['CLNT_ID', 'SESS_ID'])['CLAC1_NM'].apply(lambda x: "[%s]" % ','.join(x))
temp_series = raw3.groupby(['CLNT_ID', 'SESS_ID'])['CLAC1_NM'].agg(lambda x: list(x))
temp_df=pd.DataFrame(temp_series)
temp_df.head(10)


# In[17]:


temp2_df=temp_df.reset_index()  


# In[18]:


temp2_df.head()


# #### Phase2. SESS_ID로 정렬된 Dataframe을 역행하여 {SESS_ID: 36개의 대분류 구매 빈도 vector}의 Dictionary를 만들거에요.

# In[30]:


# 이런 식으로 empty vector 제작
vec_frame=np.zeros((1,37))


# In[22]:


# 겹치는 SESS_ID가 있어서 다른 고객 구매 패턴이 한 곳에 저장되는 것을 막기 위해
# 중복되는 SESS_ID를 리스트로 뽑아내고, 
# 최초의 SESS_ID의 구매 패턴만 딕셔너리에 저장합니다.

def check_add_key(dict, list, key,n): 
    if key in dict.keys(): 
        list=list.append(key)
    else: 
        dict[temp2_df.SESS_ID[n]]=vec_frame


# #### 변수 1 - 10-15분 소요

# In[23]:


# 변수 1 단순 빈도 Vector
n=len(temp_df)-1
prod_count_dict={}
redundant_key=[] # 중복 Session ID를 모을 겁니다.

while True:
    vec_frame=np.zeros((1,37))
    if n !=-1:
        for i in temp2_df.CLAC1_NM[n]:
            vec_frame[0][i]+=1
        check_add_key(prod_count_dict,redundant_key,temp2_df.SESS_ID[n],n)
        n=n-1
    elif n ==-1:
        print("Done")
        break


# In[28]:


#중복 Session ID가 잘 걸러졌나요?
len(prod_count_dict)+len(redundant_key)==len(temp_df)


# #### 변수 2 - 10-15분 소요

# In[29]:


# 변수 2 0,1의 Binary Vector
n=len(temp_df)-1
prod_bin_dict={}
redundant_key2=[]

while True:
    vec_frame=np.zeros((1,37))
    if n !=-1:
        for i in set(temp2_df.CLAC1_NM[n]):
            vec_frame[0][i]+=1
        check_add_key(prod_bin_dict,redundant_key2,temp2_df.SESS_ID[n],n)
        n=n-1
    elif n ==-1:
        print("Done")
        break


# In[31]:


#중복 Session ID가 잘 걸러졌나요?
len(prod_bin_dict)+len(redundant_key2)==len(temp_df)


# #### Phase3. Henry의 데이터프레임과 연결

# In[35]:


session.head()


# In[47]:


session['PD_CT_Vec']=""
session['PD_CT_Vec']=session['SESS_ID'].map(prod_count_dict)


# In[45]:


session['PD_BIN_Vec']=""
session['PD_BIN_Vec']=session['SESS_ID'].map(prod_bin_dict)


# In[48]:


session.head()


# In[50]:


session.PD_CT_Vec.isnull().sum() # 빈 값은 없습니다.


# #### 벡터 활용 시 코드 실행하는데 30분은 소요되니 Pickle 쓰세요

# In[52]:


import pickle
with open('PD_CT_Vec.pickle','wb')as handle:
    pickle.dump(prod_count_dict,handle)

with open('PD_BIN_Vec.pickle','wb')as handle:
    pickle.dump(prod_bin_dict,handle)


# In[55]:


with open('redundant_key_list.pickle','wb')as handle:
    pickle.dump(redundant_key,handle)


# ### SESS_ID 가 같지만 다른 Client여도 일단은 한명의 구매 패턴 벡터로 Mapping되었다는 문제점이 있음. 
# #### 해결 방안1 : SESS_ID 겹치는 2만개 가량의 Records를 제거한다 -> 데이터 손실, 쉬움
# #### 해결 방안2: SESS_ID 이름을 바꿔서 전부 다시 진행한다 -> 정확, 시간 소요

# ### Phase 4. Additional 시각화
