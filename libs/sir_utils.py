"""
Code adapted from: https://github.com/Lewuathe/COVID19-SIR
https://www.lewuathe.com/covid-19-dynamics-with-sir-model.html
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
from libs.obs_utils import *

def loss(point, data, s_0, i_0, r_0):
    """
    RMSE between actual confirmed cases and the estimated infectious people with given beta and gamma.
    """
    size = len(data)
    beta, gamma = point
    def SIR(t, y):
        S = y[0]
        I = y[1]
        R = y[2]
        return [-beta*S*I, beta*S*I-gamma*I, gamma*I]
    solution = solve_ivp(SIR, [0, size], [s_0,i_0,r_0], t_eval=np.arange(0, size, 1), vectorized=True)
    return np.sqrt(np.mean((solution.y[1] - data)**2))

class SirLearner(object):
    def __init__(self, confirmed_data, location, loss, predict_range, r_0, i_0, N):
        self.confirmed_data = confirmed_data
        self.location = location
        self.loss = loss
        self.predict_range = predict_range
        self.r_0 = r_0
        self.i_0 = i_0
        self.N = N
        self.s_0 = N - i_0 - r_0

    def load_confirmed(self):
        """
        Load confirmed cases from NYT data
        """
        loc_df = self.confirmed_data[self.location]
        return loc_df[loc_df != 0]

    def extend_index(self, index):
        values = index.date
        current = values[-1]
        while len(values) < self.predict_range:
            current = current + timedelta(days=1)
            values = np.append(values, current)           
        return values

    def predict(self, beta, gamma, data):
        """
        Predict how the number of people in each compartment can be changed through time toward the future.
        The model is formulated with the given beta and gamma.
        """

        new_index = self.extend_index(data.index)
        size = len(new_index)
        def SIR(t, y):
            S = y[0]
            I = y[1]
            R = y[2]
            return [-beta*S*I, beta*S*I-gamma*I, gamma*I]
        extended_actual = np.concatenate((data.values, [None] * (size - len(data.values))))
        return new_index, extended_actual, solve_ivp(SIR, [0, size], [self.s_0,self.i_0,self.r_0], t_eval=np.arange(0, size, 1))

    def train(self):
        """
        Run the optimization to estimate the beta and gamma fitting the given confirmed cases.
        """
        data = self.load_confirmed()
        optimal = minimize(
            loss, 
            [0.001, 0.001], 
            args=(data, self.s_0, self.i_0, self.r_0), 
            method='L-BFGS-B', 
            # bounds=[(0.00000001, 0.5), (0.00000001, 0.5)]
            bounds=[(0.00000001, 0.5), (0.2, 0.2)]  # constrained gamma to 1/5
            )

        beta, gamma = optimal.x
        new_index, extended_actual, prediction = self.predict(beta, gamma, data)
        df = pd.DataFrame({
            'Actual': extended_actual,
            'Susceptible': prediction.y[0],
            'Infectious': prediction.y[1],
            'Recovered': prediction.y[2]
        }, index=new_index)
        return beta, gamma, df

# N = 200
# i_0 = 1
# r_0 = 0

# zoo_data = CovidTrends(county=30063).get_covid_data()
# gal_data = CovidTrends(county=30031).get_covid_data()
# data = pd.merge(
#     zoo_data, gal_data['Gallatin'], how='inner', 
#     left_index=True, right_index=True
#     )

# l = SirLearner(data, 'Missoula', loss, 150, r_0, i_0, N)
# beta, gamma, df = l.train()
# fig, ax = plt.subplots(figsize=(8, 5))
# ax.set_title('Montana')
# df.plot(ax=ax)
# plt.show()
# df.head()
