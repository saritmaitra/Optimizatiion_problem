# -*- coding: utf-8 -*-
"""PortfolioOptimization.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Abiuym624NyGuPcAxNLaCHVEHSgabOde
"""

# Commented out IPython magic to ensure Python compatibility.
import os                               
import math                             
import numpy as np                      
import pandas as pd                     
import matplotlib.pyplot as plt        
from matplotlib import cm               
import scipy                            
import cvxpy as cp                      
from mpl_toolkits.mplot3d import Axes3D 
# %matplotlib inline
from google.colab import files

uploaded = files.upload()

df = pd.read_csv("prices.txt", parse_dates = True, index_col=0)
df.info()

"""It covers 10 years, from January 2006 to December 2016, and comprises a set of 52 popular exchange traded funds (ETFs) and the US central bank (FED) rate of return"""

df.shape

data = df.reset_index()
data.rename(columns = {'index': 'date'}, inplace=True)
data.tail()

"""## Optimization
### Constants, parameters and variables
"""

data = df.reset_index()
data.rename(columns = {'index': 'date'}, inplace=True)

# last price for each fund
last_price = data.drop(['date'], axis=1)
last_price = last_price.tail(1).to_numpy()
pd.DataFrame(last_price)

# weekly returns of last 1 year
week_ret = data[(data['date'].dt.weekday == 4) & (data['date'] >= '2016-01-01')]
week_ret = week_ret.drop(['date'], 1)
week_ret = week_ret.pct_change().dropna()

# expected return and covariance matrix
sigma = week_ret.cov().to_numpy()
mu = week_ret.mean().to_numpy()

sigma

mu

# optimization variable and parameters
x = cp.Variable(shape = df.shape[1], integer=True)
threshold = cp.Parameter(nonneg=True) # maximum portfolio variance
k = cp.Parameter(nonneg=True) # maximum allocation into one fund
# portfolio mean and variance
mean = mu.T*x
variance = cp.quad_form(x, sigma)
objective = cp.Maximize(mean) # objective function
# constraints
constraints = [x >= 0, variance <= threshold]
for pi in last_price:
    constraints = constraints + [pi*x <= k] # upper bound on single-fund allocation
prob = cp.Problem(objective, constraints)
# Solving optimization problem for each parameter combination
z_values = []
k_values = np.arange(1000, 5000, 1000)
threshold_values = np.arange(1, 5.5, 0.5)
for threshold_value in threshold_values:
    for k_value in k_values:
        threshold.value = threshold_value
        k.value = k_value
        prob.solve()
        if prob.status != 'optimal': continue
        counts = x.value.round()
        investments = last_price*counts
        returns = mu@investments[0]
        z_values.append(returns)
# The optimal objective 
prob.solve()  # Returns the optimal value.
print("status:", prob.status); print("optimal value", prob.value)

print("A dual solution corresponding to the inequality constraints is")
print(prob.constraints[0].dual_value)

"""## Objective function

Here our objective is to maximize expected portfolio return

## Solution
Initialize the optimization problem using objective function and constraints

Solve optimization problem for each parameter combination

## Optimal portfolio
optimal portfolio using highest variance and maximum single-asset allocation
"""

print(pd.DataFrame(x.value))

optimal_funds = (df.columns).values[np.where(counts > 0)]
print('Funds=>', optimal_funds); 
counts_optimal = counts[counts > 0]
print('Counts=>', counts_optimal); 
prices_optimal = np.around(last_price, 2)[0][np.where(counts > 0)]
print('Prices=>', prices_optimal); 
investments_optimal = np.around(investments, 2)[investments > 0]
print('Investments=>', investments_optimal); print()
capital_optimal = np.around(counts_optimal@prices_optimal, 2)
print('Capital=>', capital_optimal); 
risk_optimal = np.around(counts.T@sigma@counts, 2)
print('Risk=>', risk_optimal)
return_optimal = np.around(52*returns/capital_optimal, 3)
print('Return=>', return_optimal); print()

Funds = pd.DataFrame(optimal_funds)
Funds.rename(columns = {0: 'PortfolioName'}, inplace=True)
Counts = pd.DataFrame(counts_optimal)
Counts.rename(columns = {0: 'Counts'}, inplace=True)
Prices = pd.DataFrame(prices_optimal)
Prices.rename(columns = {0: 'OptimalPrices'}, inplace=True)
Investments = pd.DataFrame(investments_optimal)
Investments.rename(columns = {0: 'OptimalInvestments'}, inplace=True)
pd.concat([Funds, Counts, Prices, Investments], 1)

"""- XLE (energy sector), XLK (technology sector) and XME (metal & mining) are dominating the portfolio with > 80% of total investments. 

- expected return is based on past prices which is not a reasonable indicator of future performance.
"""