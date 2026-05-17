# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 09:50:53 2024

@author: Scott Greenwood
"""

import sys
import os
sys.path.append(r'E:\Modelica\ModelicaPy\modelicapy')
import read_dslog
import read_logTranslation

sys.path.append(r'E:\General\pythonModelica\dymola')
import filterTranslationLog

res_tran_orig = read_logTranslation.get_log_statistics(log_file=r'C:\Users\fig\Documents\Dymola\ExaDigiT\dslog_tran_orig.txt',
                                    simulator='dymola',
                                    writeToFile=True,
                                    fileName=r'C:\Users\fig\Documents\Dymola\ExaDigiT\dslog_stats_tran_orig.txt', 
                                    mode='w')
res_sim_orig = read_dslog.get_log_statistics(log_file=r'C:\Users\fig\Documents\Dymola\ExaDigiT\dslog_orig.txt',
                                    simulator='dymola',
                                    writeToFile=True,
                                    fileName=r'C:\Users\fig\Documents\Dymola\ExaDigiT\dslog_stats_orig.txt', 
                                    mode='w')


res_tran = read_logTranslation.get_log_statistics(log_file=r'C:\Users\fig\Documents\Dymola\ExaDigiT\dslog_tran.txt',
                                    simulator='dymola',
                                    writeToFile=False,
                                    fileName=r'C:\Users\fig\Documents\Dymola\ExaDigiT\dslog_stats_tran.txt', 
                                    mode='w')

unique = filterTranslationLog.main(r'C:\Users\fig\Documents\Dymola\ExaDigiT\dslog_tran.txt')