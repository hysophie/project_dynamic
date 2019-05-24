#!/usr/bin/env python
# coding: utf-8

# ### Settings

# In[1]:


import pandas as pd
import os
import re
import numpy as np


# In[2]:


os.chdir(r'C:\Users\BokyungChoi\Desktop\GrowthHackers\project_dynamic\dataset')

product = pd.read_csv('pruduct.csv', encoding='utf-8')
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


# #### SESS_ID마다 구매한 상품 쌓아 - 그 대분류 쌓아 - 대분류 구매 패턴 (빈도 / 여부)
# #### 변수 1 : 세션 내 쇼핑 Category 구매 빈도(단순 횟수)
# #### 변수 2 : 세션 내 쇼핑 Category 구매 여부(0,1 binary vec)

# In[13]:


product = product.sort_values(by=['CLNT_ID', 'SESS_ID'], axis=0)
master= master.sort_values(by='PD_C',ascending=True)


# In[14]:


raw=product.merge(master,on='PD_C',how='inner')
raw.head()


# In[15]:


#사전식으로 대분류 배열 정렬 (ㄱ으로 시작하여 ㅎ으로 끝나도록)
clac1_list=list(raw['CLAC1_NM'].unique())
clac1_list.sort()
clac1_list[0:3]


# In[16]:


CLAC1_NM_dict=dict(zip(clac1_list,range(0,37)))
CLAC1_NM_dict


# In[17]:


#대분류 한글 -> 배정된 숫자로 변경
raw2=raw.replace({"CLAC1_NM": CLAC1_NM_dict})


# ## Phase1. 
# #### Stacking 구매 상품 - 15분 소요

# In[18]:


temp_series = raw2.groupby(['CLNT_ID', 'SESS_ID'])['CLAC1_NM'].agg(lambda x: list(x))
temp_df=pd.DataFrame(temp_series)
temp_df.head(10)


# In[133]:


#변수2 위해 만들어 둔 multiindex를 column으로 돌린 temp2_df
temp2_df=temp_df.reset_index()
temp2_df.head()


# ## Phase2. 
# #### SESS_ID로 정렬된 Dataframe을 역행하여 {(CLNT_ID,SESS_ID): 36개의 대분류 구매 빈도 vector}의 Dictionary 생성. Vector 형태로 Key를 만든 이유는? Multiindex인 Dataframe.index.values하면 tuple형태로 나와서 mapping 편리하게 하기 위함임

# In[22]:


# 이런 식으로 empty vector 제작
vec_frame=np.zeros((1,37))


# #### 변수 1 - 10-15분 소요

# In[36]:


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


# In[37]:


# 벡터가 잘 만들어졌는지 확인
len(prod_count_dict)==len(temp_df)


# #### 변수 2 - 10-15분 소요

# In[144]:


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


# In[145]:


# 벡터가 잘 만들어졌는지 확인
len(prod_bin_dict)==len(temp_df)


# ## Phase3. 
# #### MultiIndex의 데이터프레임(Example_df)과 연결방법

# In[157]:


Example_df['PD_CT_Vec'] = Example_df.index.to_series().map(prod_count_dict)
Example_df['PD_BIN_Vec'] = Example_df.index.to_series().map(prod_bin_dict)


# In[162]:


# 결측치 있는지 확인
print(Example_df['PD_CT_Vec'].isnull().sum())
print(Example_df['PD_BIN_Vec'].isnull().sum())


# #### 벡터 활용 시 코드 실행하는데 30분은 소요되니 Pickle 쓰세요

# In[163]:


import pickle
with open('PD_CT_Vec.pickle','wb')as handle:
    pickle.dump(prod_count_dict,handle)

with open('PD_BIN_Vec.pickle','wb')as handle:
    pickle.dump(prod_bin_dict,handle)

