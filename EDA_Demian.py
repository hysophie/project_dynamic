import pandas as pd

Session = pd.read_csv(r'C:\DATA\L.point2019\data\Session.csv')
Pruduct = pd.read_csv(r'C:\DATA\L.point2019\data\Pruduct.csv')

Pruduct = Pruduct.sort_values('CLNT_ID')
len(Pruduct.loc[:,['CLNT_ID','SESS_ID']].drop_duplicates())

Session = Session.sort_values('CLNT_ID')
len(Session.loc[:,['CLNT_ID','SESS_ID']].drop_duplicates())

# Session과 pruduct의 고유한 키값이 동일하다. 
# pruduct에 포함되지 않지만 Session에는 포함되는 데이터가 있으면 Session의 고유한 키값이 더 많아야한다. 