# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 11:06:52 2016

@author: bohdan
"""

import pandas as pd 
from sklearn.metrics import cohen_kappa_score
from scipy.optimize import fmin_powell
from sklearn import linear_model
import json

config = json.load(open('settings.json'))

num_classes = 8

train_ohd1 = pd.read_csv(config['train_xgb'])
test_ohd1 = pd.read_csv(config['test_xgb'])
train_ohd2 = pd.read_csv(config['train_lr'])
test_ohd2 = pd.read_csv(config['test_lr'])
train_ohd3 = pd.read_csv(config['train_rf'])
test_ohd3 = pd.read_csv(config['test_rf'])
train_ohd4 = pd.read_csv(config['train_p1'])
test_ohd4 = pd.read_csv(config['test_p1'])


ftrs2 = ['Id'] + list(train_ohd2.columns[133:])
ftrs3 = ['Id'] + list(train_ohd3.columns[133:])
ftrs4 = ['Id'] + list(train_ohd4.columns[133:])

train_ohd = pd.merge(train_ohd1,train_ohd2[ftrs2],on='Id')
train_ohd = pd.merge(train_ohd,train_ohd3[ftrs3],on='Id')
train_ohd = pd.merge(train_ohd,train_ohd4[ftrs4],on='Id')

test_ohd = pd.merge(test_ohd1,test_ohd2[ftrs2],on='Id')  
test_ohd = pd.merge(test_ohd,test_ohd3[ftrs3],on='Id')  
test_ohd = pd.merge(test_ohd,test_ohd4[ftrs4],on='Id')  

        
train_ohd.fillna(-1, inplace=True)
test_ohd.fillna(-1, inplace=True)


a0 = (0.05,0.15,0.8)
a1 = (0.05,0.15,0.4,0.4)

for j in range(1,9):
    train_ohd['p%s' % (j)] = train_ohd.apply(lambda x: a1[0]*x['lr%s' % (j)] + a1[1]*x['rf%s' % (j)] + a1[2]*x['xgb%s' %(j)] + a1[3]*x['pr%s' %(j)],1)
    test_ohd['p%s' % (j)] = test_ohd.apply(lambda x: a1[0]*x['lr%s' % (j)] + a1[1]*x['rf%s' % (j)] + a1[2]*x['xgb%s' %(j)] + a1[3]*x['pr%s' %(j)],1)            

for j in range(9,14):
    train_ohd['p%s' % (j)] = train_ohd.apply(lambda x: a0[0]*x['lr%s' % (j)] + a0[1]*x['rf%s' % (j)] + a0[2]*x['xgb%s' %(j)],1)
    test_ohd['p%s' % (j)] = test_ohd.apply(lambda x: a0[0]*x['lr%s' % (j)] + a0[1]*x['rf%s' % (j)] + a0[2]*x['xgb%s' %(j)],1)
   
columns_to_drop = ['Id', 'Response', 'MedicaliHistoryi10','MedicaliHistoryi24']
features = list(train_ohd.drop(columns_to_drop, axis=1).columns[:129]) + ['p1','p2','p3','p4','p5','p6','p7','p8','p9','p10','p11','p12','p13'] 
features = list(train_ohd.drop(columns_to_drop, axis=1).columns[:129]) + ['xgb1','xgb2','xgb3','xgb4','xgb5','xgb6','xgb7','xgb8','xgb9','xgb10','xgb11','xgb12','xgb13'] 

lr = linear_model.LinearRegression()
lr.fit(train_ohd[features],train_ohd['Response'])
train_preds = lr.predict(train_ohd[features])
test_preds = lr.predict(test_ohd[features])

def digit0(xxx_todo_changeme,sr):
    '''
    Digitize test list 
    '''    
    (x1,x2,x3,x4,x5,x6,x7) = xxx_todo_changeme
    res = []
    for y in list(sr):
        if y < x1:
            res.append(1)
        elif y < x2:
            res.append(2)
        elif y < x3:
            res.append(3)
        elif y < x4:
            res.append(4)
        elif y < x5:
            res.append(5)
        elif y < x6:
            res.append(6)
        elif y < x7:
            res.append(7)
        else: res.append(8)
    return res  

def digit(xxx_todo_changeme1):
    '''
    Digitize train list
    '''
    (x1,x2,x3,x4,x5,x6,x7) = xxx_todo_changeme1
    res = []
    for y in list(train_preds):
        if y < x1:
            res.append(1)
        elif y < x2:
            res.append(2)
        elif y < x3:
            res.append(3)
        elif y < x4:
            res.append(4)
        elif y < x5:
            res.append(5)
        elif y < x6:
            res.append(6)
        elif y < x7:
            res.append(7)
        else: res.append(8)
    return res    

def train_offset(xxx_todo_changeme2):
    '''
    Finding offsets
    '''
    (x1,x2,x3,x4,x5,x6,x7) = xxx_todo_changeme2
    res = digit((x1,x2,x3,x4,x5,x6,x7))    
    return -cohen_kappa_score(train_ohd["Response"], res, weights = "quadratic")#return -quadratic_weighted_kappa(train_ohd['Response'], res)        
    
x0 = (1.5,2.9,3.1,4.5,5.5,6.1,7.1)    
offsets = fmin_powell(train_offset, x0, disp = True)
final_test_preds = digit0(offsets,test_preds)
preds_out = pd.DataFrame({"Id": test_ohd['Id'].values, "Response": final_test_preds})
print(preds_out.shape)
preds_out.to_csv(config['submission'], index=False)
#preds_out.to_csv('/media/newhd/Prudential/main/submissions/submission.csv', index=False)

#store train predictions
final_train_preds = digit0(offsets, train_preds)

train_preds_out = pd.DataFrame({"Id": train_ohd['Id'].values, "Response": final_train_preds})

#ensure directory exists
import os
os.makedirs(os.path.dirname('features/train_predictions'), exist_ok=True)
train_preds_out.to_csv('features/train_predictons', index=False)

def get_model_and_cutoffs():
    config = json.load(open('settings.json'))
    num_classes = 8

    train_ohd1 = pd.read_csv(config['train_xgb'])
    test_ohd1 = pd.read_csv(config['test_xgb'])
    train_ohd2 = pd.read_csv(config['train_lr'])
    test_ohd2 = pd.read_csv(config['test_lr'])
    train_ohd3 = pd.read_csv(config['train_rf'])
    test_ohd3 = pd.read_csv(config['test_rf'])
    train_ohd4 = pd.read_csv(config['train_p1'])
    test_ohd4 = pd.read_csv(config['test_p1'])

    ftrs2 = ['Id'] + list(train_ohd2.columns[133:])
    ftrs3 = ['Id'] + list(train_ohd3.columns[133:])
    ftrs4 = ['Id'] + list(train_ohd4.columns[133:])

    train_ohd = pd.merge(train_ohd1,train_ohd2[ftrs2],on='Id')
    train_ohd = pd.merge(train_ohd,train_ohd3[ftrs3],on='Id')
    train_ohd = pd.merge(train_ohd,train_ohd4[ftrs4],on='Id')

    test_ohd = pd.merge(test_ohd1,test_ohd2[ftrs2],on='Id')  
    test_ohd = pd.merge(test_ohd,test_ohd3[ftrs3],on='Id')  
    test_ohd = pd.merge(test_ohd,test_ohd4[ftrs4],on='Id')  

    train_ohd.fillna(-1, inplace=True)
    test_ohd.fillna(-1, inplace=True)

    a0 = (0.05, 0.15, 0.8)
    a1 = (0.05, 0.15, 0.4, 0.4)

    for j in range(1, 9):
        train_ohd[f'p{j}'] = train_ohd.apply(lambda x: a1[0]*x[f'lr{j}'] + a1[1]*x[f'rf{j}'] + a1[2]*x[f'xgb{j}'] + a1[3]*x[f'pr{j}'], axis=1)
        test_ohd[f'p{j}'] = test_ohd.apply(lambda x: a1[0]*x[f'lr{j}'] + a1[1]*x[f'rf{j}'] + a1[2]*x[f'xgb{j}'] + a1[3]*x[f'pr{j}'], axis=1)

    for j in range(9, 14):
        train_ohd[f'p{j}'] = train_ohd.apply(lambda x: a0[0]*x[f'lr{j}'] + a0[1]*x[f'rf{j}'] + a0[2]*x[f'xgb{j}'], axis=1)
        test_ohd[f'p{j}'] = test_ohd.apply(lambda x: a0[0]*x[f'lr{j}'] + a0[1]*x[f'rf{j}'] + a0[2]*x[f'xgb{j}'], axis=1)

    columns_to_drop = ['Id', 'Response', 'MedicaliHistoryi10', 'MedicaliHistoryi24']
    features = list(train_ohd.drop(columns_to_drop, axis=1).columns[:129]) + \
               ['xgb1','xgb2','xgb3','xgb4','xgb5','xgb6','xgb7','xgb8','xgb9','xgb10','xgb11','xgb12','xgb13']

    lr = linear_model.LinearRegression()
    lr.fit(train_ohd[features], train_ohd['Response'])

    train_preds = lr.predict(train_ohd[features])
    test_preds = lr.predict(test_ohd[features])

    def digit_cutoffs(cutoffs, preds):
        (x1, x2, x3, x4, x5, x6, x7) = cutoffs
        return [
            1 if y < x1 else
            2 if y < x2 else
            3 if y < x3 else
            4 if y < x4 else
            5 if y < x5 else
            6 if y < x6 else
            7 if y < x7 else
            8 for y in preds
        ]

    def train_loss(cutoffs):
        preds = digit_cutoffs(cutoffs, train_preds)
        return -cohen_kappa_score(train_ohd["Response"], preds, weights="quadratic")

    initial_cutoffs = (1.5, 2.9, 3.1, 4.5, 5.5, 6.1, 7.1)
    offsets = fmin_powell(train_loss, initial_cutoffs, disp=True)

    return lr, offsets, train_ohd[features]