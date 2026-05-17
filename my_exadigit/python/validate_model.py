# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 10:38:00 2024

@author: Vineet Kumar
"""

from __future__ import division, print_function, unicode_literals, absolute_import
import os
import numpy as np
import pandas as pd
mypath = os.path.dirname(os.path.abspath(__file__))
import utils
import copy

if __name__=='__main__':
    dataDate = '04-07-24'
    fname = 'result.pickle'
    startPlotTime = 0.0  
    maxPlotTime = 86400
    
    # Read Simulation results
    fileName = os.path.join(mypath, 'temp', fname)
    df_pred = df = pd.read_pickle(fileName)
    df_pred = df_pred[(df_pred['time'] >= startPlotTime) & 
                      (df_pred['time'] <= maxPlotTime)]
    
    # Read fac. Telemetry data
    facTeleFiles = ['facility_data_30 Sec.csv',
                    'facility_data_1 Min.csv',
                    'facility_data_2 Min.csv',
                    'facility_data_10 Min.csv',
                    'facility_data_HTWPS.csv',
                    'facility_data_CTWPS.csv',
                    'facility_data_EHXs.csv',
                    'facility_data_CT Cells.csv'
                    ]
    
    time_resampled = np.linspace(startPlotTime, maxPlotTime, int(np.floor(maxPlotTime/15))+1, dtype=int)

###################################################extractprocedures###############################
    df_fac_data = utils.extrFacData(facTeleFiles=facTeleFiles, 
                                    dataDate=dataDate,
                                    startPlotTime=startPlotTime,
                                    maxPlotTime=maxPlotTime,
                                    time_resampled=time_resampled
                                    )
    
###################################################Plot procedures#################################
    utils.plotFac(df_fac_data = copy.deepcopy(df_fac_data), 
                  df_pred = copy.deepcopy(df_pred), 
                  startPlotTime = startPlotTime,
                  maxPlotTime = maxPlotTime
                 )
