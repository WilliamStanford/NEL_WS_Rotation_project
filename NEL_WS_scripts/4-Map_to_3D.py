#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 14:43:03 2019

@author: williamstanford
"""
import numpy as np
import os 
import matplotlib.pyplot as plt
import pandas as pd 
from mpl_toolkits.mplot3d import Axes3D

from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_predict

#%%
#path = '/home/nel-lab/Desktop/WS_tests_for_DLC2/calibration2/'
path = '/Applications/NoniCloud Desktop/GiovannucciLab/cal_images_2' 
os.chdir(path)
rootDirectory = path

#%%  
def Build_Model(coordinatePath):
    
    ''' 
    uses the location of your calibration points in the real world and fits a polynomial 
    to this data to project the pixel locations in each image to your real world coordinate system
    '''  
    
    All_Data = pd.read_csv(coordinatePath) 
    
    X_train_full, X_test, y_train_full, y_test = train_test_split( 
            All_Data.iloc[:,:-3], All_Data.iloc[:,-3:], random_state=42,  test_size = 0.25)
    
#    v = All_Data.shape[0]//2
#    X_valid, X_train = X_train_full[:v], X_train_full[v:]
#    y_valid, y_train = y_train_full[:v], y_train_full[v:]
    
    svm = SVR(kernel="poly", degree=2, C=1500, epsilon=0.01, gamma="scale")
    regr = MultiOutputRegressor(svm)
    regr.fit(X_train_full, y_train_full)
    
    test_predictions = regr.predict(X_test)
    test_MSE = mean_squared_error(test_predictions, y_test)
    print('Test MSE: ' + str(test_MSE))
    
    X = All_Data.iloc[:,:-3]
    Y = All_Data.iloc[:,-3:]
    
    CV_predictions = cross_val_predict(regr, X, Y, cv=10)
    MSE = mean_squared_error(CV_predictions, Y)
    
    print('Mean squared error: ' + str(MSE))
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for x in range(CV_predictions.shape[0]):
        ax.scatter(CV_predictions[x,0], CV_predictions[x,1], CV_predictions[x,2], 
                   color = 'blue')
        ax.scatter(All_Data.iloc[x,-3], All_Data.iloc[x,-2], All_Data.iloc[x,-1], 
                   color = 'red')

    return regr, X, Y, CV_predictions
    
#%%
def PreProcess_DLC_data(df):
    
    '''
    We preprocess the CSV's output by DeepLabCut
        1. Rename each column with the bodypart and coordinate (x or y)
        2. delete redundant rows and columns 
    '''
    
    for y in range (df.shape[1]):        
        df.rename(columns={df.columns[y]:df.iloc[0,y]+'_'+df.iloc[1,y]}, inplace=True)
        
    df2 = df.iloc[2:,1:]
    
    li_columns = [col for col in df2.columns if 'likelihood' in col]
    df2 = df2.drop(columns=li_columns)
        
    return df2

#%%
    '''
    need to make sure that columns in each dataframe align correctly. These two
    functions enable us to compare columns in two dataframes and delete the extra 
    '''
    
def Diff(li1, li2):       
        return (list(set(li1) - set(li2))) 

#%%
def Standardize_columns(df1,df2):
    cols1 = df1.columns.tolist()
    cols2 = df2.columns.tolist()
    
    # find the differences between the columns, test both ways, if one df has
    # columns which are a subset of the second, then reverse the order of subtraction
    # to find the difference 
    col_diff = Diff(cols1,cols2)
    if len(col_diff) == 0:
        col_diff = Diff(cols2,cols1)
    
    
    if len(col_diff) > 0: 
        
        a = len(col_diff)
        for i in range(a):
            if col_diff[i] in df1.columns:
                df1 = df1.drop(columns=col_diff[i])
            if col_diff[i] in df2.columns:
                df2 = df2.drop(columns=col_diff[i])
    
    # reorder columns to follow order of the first dataframe
    df2 = df2[df1.columns]
            
    return df1,df2

#%% 3 Camera 3D prediction 
def Predict_Real_Coordinates(df1, df2, df3, bodyparts, numCameras, regr):
    
    '''
    Use model and data generated by DeepLabCut to predict the 3D locations of every
    bodypart of interest
    '''  
    rows = df1.shape[0]
    columns = 2*numCameras
    bparts = bodyparts
    
    test_data = np.zeros((rows, columns*bparts))
    
    for r in range(bparts):
        test_data[:,6*r] = df1.iloc[:,2*r]
        test_data[:,6*r+1] = df1.iloc[:,2*r+1]
        
        test_data[:,6*r+2] = df2.iloc[:,2*r]
        test_data[:,6*r+3] = df2.iloc[:,2*r+1]
        
        test_data[:,6*r+4] = df3.iloc[:,2*r]
        test_data[:,6*r+5] = df3.iloc[:,2*r+1]
    
    Predictions = np.zeros((rows,3*bparts))
    
    for i in range(bparts):
        Predictions[:,3*i:(3*i+3)] = regr.predict(test_data[:,6*i:(6*i+6)])
        
    return Predictions

#%% 2 Camera 3D prediction 
def Predict_Real_Coordinates_2cam(df1, df2, bodyparts, numCameras, regr):
    
    # make sure all dataframes share the same columns and delete extras
    df1,df2 = Standardize_columns(df1,df2)
    
    # reorder columns to follow order of the first dataframe
    df2 = df2[df1.columns]
    
    '''
    Use model and data generated by DeepLabCut to predict the 3D locations of every
    bodypart of interest
    '''
        
    rows = df1.shape[0]
    columns = 2*numCameras
    bparts = bodyparts
    
    test_data = np.zeros((rows, columns*bparts))
    
    for r in range(bparts):
        test_data[:,4*r] = df1.iloc[:,2*r]
        test_data[:,4*r+1] = df1.iloc[:,2*r+1]
        
        test_data[:,4*r+2] = df2.iloc[:,2*r]
        test_data[:,4*r+3] = df2.iloc[:,2*r+1]

    Predictions = np.zeros((rows,3*bparts))
    
    for i in range(bparts):
        Predictions[:,3*i:(3*i+3)] = regr.predict(test_data[:,4*i:(4*i+4)])
        
    return Predictions

#%% Plot first 300 frames 
def Plot_Bodyparts(Predictions, bodyparts):
    
    bparts = bodyparts    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for y in range(300):
    #for y in range(Predictions.shape[0]): # to plot full video
        plt.cla()
        for x in range(bparts):
            i = 3*x
            j = 3*x+1
            k = 3*x+2
            z = 2900
            ax.scatter(Predictions[z+y,i], Predictions[z+y,j], 
                       Predictions[z+y,k], color = 'blue')
            ax.set_xlim([0,40])
            ax.set_ylim([0,60])
            ax.set_zlim([-20,15])
            
        plt.pause(0.005)
        
    return 

#%% BUILD MODELS 
''' 
uses the location of your calibration points in the real world and fits a polynomial 
to this data to project the pixel locations in each image to your real world coordinate system
'''

#%% M1 - for three cameras - front feet
#coordinatePath_1 = '/home/nel-lab/Desktop/WS_tests_for_DLC2/calibration2/model_1_coordinates.csv'
coordinatePath_1 = '/Applications/NoniCloud Desktop/GiovannucciLab/cal_images_2/model_1_coordinates.csv'
m1_regr, X, Y, cv_predictions = Build_Model(coordinatePath_1)

#%% PREPROCESS DLC DATA
'''
We preprocess the CSV's output by DeepLabCut
    1. Rename each column with the bodypart and coordinate (x or y)
    2. delete redundant rows and columns 
'''
#%% M1 
front_left = pd.read_csv('front_left.csv') # The name here has been edited - these files are from the output of DLC after analyzing a video                  
front_right = pd.read_csv('front_right.csv') 
bot = pd.read_csv('bot.csv')

mod_front_left = PreProcess_DLC_data(front_left)
mod_front_right = PreProcess_DLC_data(front_right)
mod_bot = PreProcess_DLC_data(bot)

mod_front_left.to_csv('mod_front_left.csv', index=False)
mod_front_right.to_csv('mod_front_right.csv', index=False)
mod_bot.to_csv('mod_bot.csv', index=False)

#%% PREDICT REAL WORLD COORDINATES OF DLC DATA
'''
Use model and data generated by DeepLabCut to predict the 3D locations of every
bodypart of interest
'''

#%% M1
numCameras = 3
bodyparts = 10

mod_bot = pd.read_csv('mod_bot.csv') 
mod_front_right = pd.read_csv('mod_front_right.csv') 
mod_front_left = pd.read_csv('mod_front_left.csv') 

# this will delete any columns that are shared by all dataframes
mod_front_left, mod_front_right = Standardize_columns(mod_front_left, mod_front_right)
mod_front_right, mod_bot = Standardize_columns(mod_front_right, mod_bot)

m1_predictions = Predict_Real_Coordinates(mod_front_left, mod_front_right, 
                                          mod_bot, bodyparts, numCameras, m1_regr)

m1_Predictions = pd.DataFrame(m1_predictions)
m1_Predictions.to_csv('m1_Predictions.csv', index=False)

#%% PLOT BODYPARTS
'''
Plot locations of each bodypart - only plots first 300 frames
'''

#%% M1
bodyparts = 10
m1_Predictions = pd.read_csv('m1_Predictions.csv') 
m1_Predictions = m1_Predictions.to_numpy() 
Plot_Bodyparts(m1_Predictions, bodyparts)

#%% For remaining models, same as above
'''
A. Build the model
B. Preprocess DLC data
C. Predict 3D locations
D. Plot body parts 
'''

#%% M2 - for three cameras - back feet
coordinatePath_2 = '/home/nel-lab/Desktop/WS_tests_for_DLC2/calibration2/model_2_coordinates.csv'
m2_regr, X, Y, cv_predictions = Build_Model(coordinatePath_2)

#%% M2-a - for two cameras - back right foot - I have not built this model yet but the videos and images have been taken to do so
coordinatePath_2a = '/home/nel-lab/Desktop/WS_tests_for_DLC2/calibration2/model_2_coordinates-a.csv'
m2a_regr, X, Y, cv_predictions = Build_Model(coordinatePath_2a)

#%% M2-b - for two cameras - back left foot - I have not built this model yet but the videos and images have been taken to do so
coordinatePath_2b = '/home/nel-lab/Desktop/WS_tests_for_DLC2/calibration2/model_2_coordinates-b.csv'
m2b_regr, X, Y, cv_predictions = Build_Model(coordinatePath_2b)

#%% M2
bot = pd.read_csv('bot.csv') # The name here has been edited - these files are from the output of DLC after analyzing a video
back_right = pd.read_csv('back_right.csv') 
back_left = pd.read_csv('back_left.csv') 

mod_back_left = PreProcess_DLC_data(back_left)
mod_back_right = PreProcess_DLC_data(back_right)
mod_bot = PreProcess_DLC_data(bot)

mod_bot.to_csv('mod_bot.csv', index=False)
mod_front_left.to_csv('mod_back_left.csv', index=False)
mod_front_right.to_csv('mod_back_right.csv', index=False)

#%% M2
numCameras = 3
bodyparts = 10

mod_bot = pd.read_csv('mod_bot.csv') 
mod_back_left = pd.read_csv('mod_back_left.csv') 
mod_back_right = pd.read_csv('mod_back_right.csv') 

# this will delete any columns that are shared by all dataframes
mod_back_left, mod_back_right = Standardize_columns(mod_back_left, mod_back_right)
mod_back_right, mod_bot = Standardize_columns(mod_back_right, mod_bot)

m2_predictions = Predict_Real_Coordinates(mod_back_left, mod_back_right, mod_bot,  
                                          bodyparts, numCameras, m2_regr)

m2_Predictions = pd.DataFrame(m2_predictions)
m2_Predictions.to_csv('m2_Predictions.csv', index=False)

#%% M2-a
numCameras = 2
bodyparts = 6

mod_bot = pd.read_csv('mod_bot.csv') 
mod_back_left = pd.read_csv('mod_back_left.csv') 

# this will delete any columns that are shared by all dataframes
mod_back_left, mod_bot= Standardize_columns(mod_back_left, mod_bot)

m2a_predictions = Predict_Real_Coordinates_2cam(mod_back_left, mod_bot, bodyparts, 
                                                numCameras, m2a_regr)

m2a_Predictions = pd.DataFrame(m2a_predictions)
m2a_Predictions.to_csv('m2a_Predictions.csv', index=False)

#%% M2-b
numCameras = 2
bodyparts = 6

mod_bot = pd.read_csv('mod_bot.csv') 
mod_back_right = pd.read_csv('mod_back_right.csv') 

# this will delete any columns that are shared by all dataframes
mod_back_right, mod_bot = Standardize_columns(mod_back_right, mod_bot)

m2b_predictions = Predict_Real_Coordinates_2cam(mod_back_right, mod_bot, bodyparts, 
                                                numCameras, m2b_regr)

m2b_Predictions = pd.DataFrame(m2b_predictions)
m2b_Predictions.to_csv('m2b_Predictions.csv', index=False)


#%% M2
bodyparts = 10
m2_Predictions = pd.read_csv('m2_Predictions.csv') 
m2_Predictions = m2_Predictions.to_numpy() 
Plot_Bodyparts(m1_Predictions, bodyparts)

#%% M2-a
bodyparts = 6
m2a_Predictions = pd.read_csv('m2a_Predictions.csv') 
m2a_Predictions = m2a_Predictions.to_numpy() 
Plot_Bodyparts(m2a_Predictions, bodyparts)

#%% M2-b
bodyparts = 6
m2b_Predictions = pd.read_csv('m2b_Predictions.csv') 
m2b_Predictions = m2b_Predictions.to_numpy() 
Plot_Bodyparts(m2b_Predictions, bodyparts)

