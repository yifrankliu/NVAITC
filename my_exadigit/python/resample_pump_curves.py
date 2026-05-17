# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 08:48:11 2024

@author: Scott Greenwood
"""

x = [0,0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.01,
            0.011,0.012,0.013,0.014,0.015,0.016,0.017,0.018,0.019,0.02,0.021,0.022,
            0.023,0.024,0.025,0.026,0.027,0.028,0.029,0.03,0.031,0.032,0.033,0.034,
            0.035,0.036,0.037,0.038,0.039,0.04]
y = [64.112,64.5521,64.9368,
            65.2661,65.54,65.7585,65.9215,66.0292,66.0815,66.0784,66.0199,65.906,
            65.7367,65.512,65.2319,64.8964,64.5054,64.0591,63.5574,63.0003,62.3878,
            61.7199,60.9966,60.2179,59.3838,58.4943,57.5493,56.549,55.4933,54.3822,
            53.2157,51.9938,50.7165,49.3838,47.9957,46.5522,45.0532,43.4989,41.8892,
            40.2241,38.5036]


import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

def fit_and_predict_cubic(x, y, new_x):
    # Convert x and y to numpy arrays
    x = np.array(x)
    y = np.array(y)
    new_x = np.array(new_x)
    
    # Fit the cubic spline model
    cs = CubicSpline(x, y)
    
    # Predict new y values
    new_y = cs(new_x)
    
    return new_y

def fit_and_predict_poly(x, y, new_x, degree=2):
    # Fit a polynomial of the specified degree
    coeffs = np.polyfit(x, y, degree)
    
    # Create a polynomial function with the coefficients
    poly = np.poly1d(coeffs)
    
    # Predict new y values
    new_y = poly(new_x)
    
    return new_y, coeffs


new_x = np.linspace(x[0],x[-1],11)

# new_y = fit_and_predict_cubic(x, y, new_x)
new_y, coeffs = fit_and_predict_poly(x, y, new_x)

# Create a 2D array with new_y first and then new_x, and reverse the order
yx = np.array([new_y, new_x]).T[::-1]

print("New x values:", new_x)
print("Predicted y values:", new_y)

# Plotting for visualization
plt.scatter(x, y, color='blue', label='Original')
plt.plot(new_x, new_y, color='red', label='Predictions')
plt.xlabel('x values')
plt.ylabel('y values')
plt.legend()
plt.show()