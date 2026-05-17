# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 10:38:00 2024

@author: Vineet Kumar
"""

from __future__ import print_function, absolute_import, division
import os
from tkinter import font
from xml.sax import default_parser_list
mypath = os.path.dirname(os.path.abspath(__file__))
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

###################################################Read procedures###################################################
def extract_data_csv(fileName, skiprows, header):
    """ Read passed csv file path
        @ In, filename, dataframe, facility telemetry data 
        @ In, skiprows, int, number of rows to be skipped
        @ In, header, list, header of output dataframe
        @ Out, df, dataframe, read file returned as a dataframe
    """
    df = pd.read_csv(fileName, skiprows=skiprows, header=header)
    df = df.rename(columns={df.columns[0]: 'time'})
    df = df.dropna()
    print("Column headings:")
    print(df.columns.tolist())
    print(df.head())
    return df

def extrFacData(facTeleFiles, dataDate, startPlotTime, maxPlotTime, time_resampled):
    """ Extract facility data and combine to a single dataframe
        @ In, facTeleFiles, list, facility telemetry data file names 
        @ In, dataDate, str, telemetry data date as str
        @ In, startPlotTime, float, starting plot time in sec. 
        @ In, maxPlotTime, float, maximum plot time in sec.
        @ In, time_resampled, array, resampled time array in sec.
        @ Out, df_fac_data, dataframe, dataframe with the combined facility data
    """
    df_fac_data = []
    
    for file in facTeleFiles:
        fileName = os.path.join(mypath, 'data', dataDate, file)
        df = extract_data_csv(fileName, skiprows=None, header=0)
        df = df[(df['time'] >= startPlotTime) 
                & (df['time'] <= maxPlotTime)]
        dfmod = df.reset_index(drop=True)
        dfmod['time'] = dfmod['time'] - dfmod.loc[0, "time"]
        dfmod = resampledf(df = dfmod, time_resampled = time_resampled)
        df_fac_data.append(dfmod)
    return df_fac_data

###################################################misc procedures###################################################
def convertToSec(df):
    """ Convert datetime to sec. w.r.t to starting time
        @ In, df, dataframe, data 
        @ Out, time_delta, list, delta time list in sec.
    """
    time_delta = []
    data_time = df[df.columns[0]]
    data_time = pd.to_datetime(data_time)
    for i in range(0, len(data_time), 1):
        time_delta.append(float((data_time.iloc[i]-data_time.iloc[0]).total_seconds()))
    return time_delta

def findKey(df_fac_data, key):
    """ Match key and return idx 
        @ In, df_fac_data, dataframe, facility telemetry data 
        @ In, key, str, key to be matched
        @ Out, idx, int, dataframe where key is matched 
    """
    for idx in range(len(df_fac_data)):
        if key in df_fac_data[idx].keys():
            return idx

def resampledf(df, time_resampled):
    """ Match key and return idx 
        @ In, None
        @ Out, CDU_names, list, list of CDU names
    """
    df.set_index('time',inplace =True)
    df = df.reindex(df.index.union(time_resampled)).interpolate('values').loc[time_resampled]
    df = df.reset_index()
    return df

###################################################Plot procedures###################################################
def plotFac(df_fac_data, df_pred, startPlotTime, maxPlotTime):
    """ Generate and save sep. plots of facility Prediction vs telemetry.
        @ In, df_fac_data, dataframe, Fac. Telemetry data 
        @ In, df_pred, dataframe, Output predictions dat
        @ In, startPlotTime, float, starting plot time in sec.
        @ In, maxPlotTime, float, maximum plot time in sec.
        @ Out, None
    """   
    plotDataVars = {'HTW': ['HTWR AVG', 'HTWS AVG', 'HTW Flow', 'PTR-07', 'PTS-07', 'HTWP SPD', 'HTWPs', 'EHXs'],
                    'CTW': ['CTWR AVG', 'CTWS AVG', 'CTW Flow', 'PT-04A', 'DPT-04B', 'CTWP SPD', 'CTWPs', 'CT Cells']}

    plotPredVars = {'HTW': [
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.T_fac_htw_r_C',
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.T_fac_htw_s_C',
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.V_flow_htw_GPM',
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.p_fac_htw_r_psig',
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.p_fac_htw_s_psig',
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.N_HTWP',
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.n_HTWPs',
                            'simulator[1].centralEnergyPlant[1].hotWaterLoop[1].summary.n_EHXs'
                            ],
                    'CTW': [
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.T_fac_ctw_r_C',
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.T_fac_ctw_s_C',
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.V_flow_ctw_GPM',
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.p_fac_ctw_r_psig',
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.p_fac_ctw_s_psig',
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.N_CTWP',
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.n_CTWPs',
                            'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].summary.n_CTs'
                            ]
                    }
    
    plotSaveVars = {'HTW': ['T_fac_Out[1]','T_fac_Out[2]','Q_fac_Out[1]','p_fac_Out[1]','p_fac_Out[2]', 
                            'N_HTWP_Out[1]', 'n_HTWPs_Out[1]', 'n_EHXs_Out[1]'],
                    'CTW': ['T_fac_Out[3]','T_fac_Out[4]','Q_fac_Out[2]','p_fac_Out[3]','p_fac_Out[4]', 
                            'N_CTWP_Out[1]', 'n_CTWPs_Out[1]', 'n_CTs_Out[1]']}

    y_labels = [r'$\mathrm{Ret. Temp.}\ [^{o} \mathrm{C}] $', 
                r'$\mathrm{Sup. Temp.}\ [^{o} \mathrm{C}] $',
                'Q [GPM]',
                'Ret. Pres. [psig]',
                'Sup. Pres. [psig]',
                'Rel. Pump speed [%]',
                'Pump Staging [-]',
                'EHX Staging [-]'
                ]
    labels = ['return temperature', 'supply temperature', 'vol. flow rate', 
              'return pressure', 'supply pressure', 'rel. pump speed', 'pump staging', 
              'EHX staging', 'CT staging']
    # Set separate font sizes
    title_font_size = 14
    label_font_size = 24
    tick_font_size = 20
    text_font_size = 12

    df_pred = df_pred[(df_pred['time'] >= 1.0 + startPlotTime) & (df_pred['time'] <= maxPlotTime)]
    
    for key in list(plotDataVars.keys()):
        for idx, y_label in enumerate(y_labels):
            fig, ax = plt.subplots(figsize=(6,6))
            fig.tight_layout()
            plt.title('Time Series Predictions - Facility ' + key + ' ' + labels[idx], fontsize=title_font_size)
            ax.set_xlabel('Time [hr]')
            # 
            matchedIdx = findKey(df_fac_data, list(plotDataVars[key])[idx])
            df_fac_data[matchedIdx] = df_fac_data[matchedIdx][(df_fac_data[matchedIdx]['time'] >= 1.0 + startPlotTime) & (df_fac_data[matchedIdx]['time'] <= maxPlotTime)]
            y_data = np.array(df_fac_data[matchedIdx][list(plotDataVars[key])[idx]])
            y_pred = np.array(df_pred[plotPredVars[key][idx]])
            if 'N_CTWP' in plotPredVars[key][idx]:
                y_data =  (y_data *0.45 + 15)*100/60
            if plotPredVars[key][idx].endswith('_C'):
                y_data =  (y_data - 32.0)*5/9 #F to C
                # y_pred =  y_pred - 273.15 #K to C
            if 'Staging' in y_label:
                plt.plot(df_fac_data[matchedIdx]['time']/3600.0, y_data, color = 'k', markersize=3, marker='s', markerfacecolor='none', ls='--', label='Telemetry')
                plt.plot(df_pred['time']/3600.0, y_pred, color = 'r', ls='--',label='Prediction')
            elif key == 'CTW' and 'p_fac_ctw_s_psig' in plotPredVars[key][idx]:
                y_data =  np.zeros(len(y_pred)) # Pressure sensor not working at CTWS
                plt.plot(df_fac_data[matchedIdx]['time']/3600.0, y_data, color = 'k', markersize=1, marker='s', markerfacecolor='none', ls='-',label='')    
                plt.plot(df_pred['time']/3600.0, y_pred, color = 'r', markersize=1, marker='o',  markerfacecolor='none', ls='-',label='Prediction')
            else:
                plt.plot(df_fac_data[matchedIdx]['time']/3600.0, y_data, color = 'k', markersize=1, marker='s', markerfacecolor='none', ls='-',label='Telemetry')    
                plt.plot(df_pred['time']/3600.0, y_pred, color = 'r', markersize=1, marker='o',  markerfacecolor='none', ls='-',label='Prediction')
            
            plt.xlabel('Time [hr]', fontsize=label_font_size)
            y0 = min(min(y_data), min(y_pred))*0.90
            y1 = max(max(y_data), max(y_pred))*1.10
            plt.minorticks_on()
            plt.xticks(fontsize=tick_font_size)
            plt.yticks(fontsize=tick_font_size)
            if 'Temp' in y_label:
                plt.ylabel(r'$\mathrm{Temperature}\ [^{o} \mathrm{C}] $', fontsize=label_font_size)
                plt.text((startPlotTime+(maxPlotTime-startPlotTime)*0.03)/3600.0, (y1-y0)*0.93 + y0, r'RMSE Temperature $[^{o} \mathrm{C}]$ = %8.3e' % (np.sqrt(np.mean((y_data-y_pred)**2))),fontsize=text_font_size)
            elif 'GPM' in y_label:
                plt.ylabel('Q [GPM]', fontsize=label_font_size)
                plt.text((startPlotTime+(maxPlotTime-startPlotTime)*0.03)/3600.0, (y1-y0)*0.93 + y0, 'RMSE Vol. flow rate [GPM] = {:8.3e}'.format(np.sqrt(np.mean((y_data-y_pred)**2))),fontsize=text_font_size)
            elif 'psig' in y_label:
                plt.ylabel('Pressure [psig]', fontsize=label_font_size)
                if key == 'CTW' and 'p_fac_ctw_s_psig' in plotPredVars[key][idx]:
                    # Pressure sensor not working at CTWS
                    y0 = min(y_pred)*0.90
                    y1 = max(y_pred)*1.10
                else:
                    plt.text((startPlotTime+(maxPlotTime-startPlotTime)*0.03)/3600.0, (y1-y0)*0.95 + y0, 'RMSE [psig] = {:8.3e}'.format(np.sqrt(np.mean((y_data-y_pred)**2))),fontsize=text_font_size)
                    plt.text((startPlotTime+(maxPlotTime-startPlotTime)*0.03)/3600.0, (y1-y0)*0.90 + y0, 'MAE [psig] = {:8.3e}'.format(np.mean(np.abs(y_data-y_pred))),fontsize=text_font_size)
            elif '%' in y_label:
                y0 = 0.0
                y1 = 100.0
                plt.ylabel('N [%]', fontsize=label_font_size)
                plt.text((startPlotTime+(maxPlotTime-startPlotTime)*0.03)/3600.0, (y1-y0)*0.93 + y0, 'RMSE [%] = {:8.3e}'.format(np.sqrt(np.mean((y_data-y_pred)**2))),fontsize=text_font_size)
            elif 'Pump Staging' in y_label:
                y0 = 0
                y1 = 5
                plt.ylabel('No. of pumps staged [-]', fontsize=label_font_size)
                plt.text((startPlotTime+(maxPlotTime-startPlotTime)*0.03)/3600.0, (y1-y0)*0.93 + y0, 'RMSE No. [-] = {:8.3e}'.format(np.sqrt(np.mean((y_data-y_pred)**2))),
                         fontsize=text_font_size)
                plt.minorticks_off()
                ax.set_yticks([0, 1, 2, 3, 4, 5])
            elif 'EHX Staging' in y_label:
                y0 = 0
                y1 = 5
                plt.ylabel('No. of EHXs staged [-]', fontsize=label_font_size)
                plt.text((startPlotTime+(maxPlotTime-startPlotTime)*0.03)/3600.0, (y1-y0)*0.93 + y0, 'RMSE No. [-] = {:8.3e}'.format(np.sqrt(np.mean((y_data-y_pred)**2))),
                         fontsize=text_font_size)
                plt.minorticks_off()
                ax.set_yticks([0, 1, 2, 3, 4, 5])

            ax.set_ylim(y0, y1)
            plt.legend(frameon=False, fontsize=text_font_size, loc='upper right')
            dirpath = os.path.join(mypath, 'temp', 'validate_plots')
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            plt.savefig(os.path.join(mypath, 'temp', 'validate_plots', 'data_vs_pred_fac_' + plotSaveVars[key][idx] + '.png'), dpi=600, format='png',bbox_inches='tight')
            plt.close()
    
    fig, ax = plt.subplots(figsize=(6,6))
    fig.tight_layout()
    plt.title('Time Series Predictions - Facility ' + key + ' CT staging', fontsize=title_font_size)
    ax.set_xlabel('Time [hr]')
    matchedIdx = findKey(df_fac_data, list(plotDataVars[key])[-1])
    df_fac_data[matchedIdx] = df_fac_data[matchedIdx][(df_fac_data[matchedIdx]['time'] >= 1.0) & (df_fac_data[matchedIdx]['time'] <= maxPlotTime)]
    y_data = np.array(df_fac_data[matchedIdx][list(plotDataVars[key])[-1]])
    y_pred = np.array(df_pred[plotPredVars[key][-1]])
    plt.plot(df_fac_data[matchedIdx]['time']/3600.0, y_data, color = 'k', markersize=1, marker='s', markerfacecolor='none', ls='-',label='Telemetry')    
    plt.plot(df_pred['time']/3600.0, y_pred, color = 'r', markersize=1, marker='o',  markerfacecolor='none', ls='-',label='Prediction')
    plt.xlabel('Time [hr]', fontsize=label_font_size)
    y0 = min(min(y_data), min(y_pred))*0.90
    y1 = max(max(y_data), max(y_pred))*1.10
    plt.minorticks_on()
    plt.xticks(fontsize=tick_font_size)
    plt.yticks(fontsize=tick_font_size)
    plt.ylabel('No. of CTs staged [-]', fontsize=label_font_size)
    plt.text((startPlotTime+(maxPlotTime-startPlotTime))*0.03/3600.0, (y1-y0)*0.93 + y0, 'RMSE No. [-] = {:8.3e}'.format(np.sqrt(np.mean((y_data-y_pred)**2))),
                fontsize=text_font_size)
    plt.minorticks_off()
    ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16])
    ax.set_ylim(y0, y1)
    plt.legend(frameon=False, fontsize=text_font_size, loc='upper right')
    plt.savefig(os.path.join(mypath, 'temp', 'validate_plots', 'data_vs_pred_fac_' + plotSaveVars[key][-1] + '.png'), dpi=600, format='png',bbox_inches='tight')
    plt.close()     