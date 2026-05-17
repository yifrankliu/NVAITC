# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 16:48:10 2024

@author: Scott Greenwood
"""

import matplotlib.pyplot as plt
from buildingspy.io.outputfile import Reader
import matplotlib.pyplot as plt
import numpy as np
# Path to .mat file
resultPath = r'C:\Users\fig\Documents\Dymola\ExaDigiT\Simulator.mat'

nComputeBlocks = 25
nCabinets = 3
nCentralEnergyPlants = 1
nCoolingTowerLoops = 1
nSimulators = 1
nDatacenters = 1

# for m in range(nCabinets) for k in range(nComputeBlocks) for j in range(nDatacenters) for i in range(nSimulators)]

varNames = [f'simulator[{i+1}].datacenter[{j+1}].plenum_inlet.port_b[{k+1}].m_flow'
                  for k in range(nComputeBlocks) for j in range(nDatacenters) for i in range(nSimulators)]

varNames = [f'simulator[1].centralEnergyPlant[1].coolingTowerLoop[1].coolingTower[{m+1}].plenum_outlet.port_a[{n+1}].m_flow'
                  for n in range(4) for m in range(4) for k in range(1) for j in range(1) for i in range(1)]

r = Reader(resultPath,'dymola')
results = {}
for var in varNames:
    time, temp = r.values(var)
    results[var] = temp        
    
    
fig, ax = plt.subplots()
for key in results.keys():
    ax.plot(time, results[key], label=key)
    
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})#, ncol=np.ceil(len(results.keys())/20))
fig.tight_layout()

#%%
varNames = r.varNames(r'.*\.port_a\.m_flow$')

fig, ax = plt.subplots()
results_issue = {}
for var in varNames:
    time, temp = r.values(var)
    if np.any(temp[22000:] < 0.1):
        results_issue[var] = temp
        ax.plot(time, temp, label=var)
    
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
fig.tight_layout()