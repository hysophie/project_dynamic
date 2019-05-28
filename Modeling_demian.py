import pickle
import xgboost as xgb
from time import time


with open('C:/DATA/L.point2019/derivation_data/train_set.pickle', 'rb') as f:
    train_set = pickle.load(f)
    
with open('C:/DATA/L.point2019/derivation_data/test_set.pickle', 'wb') as f:
    test_set = pickle.load(f)

xindx = list(train_set).copy().remove('Y')

train_y = train_set.loc[:,'Y']
train_X = train_set.drop(['Y','TOT_SESS_HR_V_x', 'PD_CT_Vec', 'PD_BIN_Vec', 'TOT_SESS_HR_V_y'], axis=1)

test_y = test_set.loc[:,'Y']
test_X = test_set.drop(['Y','TOT_SESS_HR_V_x', 'PD_CT_Vec', 'PD_BIN_Vec', 'TOT_SESS_HR_V_y'], axis=1)



start = datetime.now()
gbm = xgb.XGBClassifier(max_depth=3, n_estimators=300, learning_rate=0.05).fit(train_X, train_y)
predictions = gbm.predict(test_X)
end = datetime.now()

sum(test_y == predictions)/len(predictions)
