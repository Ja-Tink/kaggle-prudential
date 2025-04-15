# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 17:47:00 2016

@author: bohdan
"""

import os

if __name__ == '__main__':
    exec(compile(open('logRegression.py', "rb").read(), 'logRegression.py', 'exec'))
    print('Logistic Regression is done')

    exec(compile(open('randomForest.py', "rb").read(), 'randomForest.py', 'exec'))
    print('Random Forest Classifier is done')

    exec(compile(open('xgboost_binary.py', "rb").read(), 'xgboost_binary.py', 'exec'))
    print('Xgboost binary is done')
    
    exec(compile(open('xgboost_multisoft.py', "rb").read(), 'xgboost_multisoft.py', 'exec'))
    print('Xgboost multisoft is done')
    

    