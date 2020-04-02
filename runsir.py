"""
Make sure to run this before deployment
"""

from libs.sir_utils import *
from libs.obs_utils import *
from datetime import datetime
import glob
import os

# Bring in data
zoo_data = CovidTrends(county=30063).get_covid_data()
gal_data = CovidTrends(county=30031).get_covid_data()
data = pd.merge(zoo_data, gal_data['Gallatin'], how='inner', left_index=True, right_index=True)

# Move existing model result data
# date = data.index[-1].strftime("%Y%m%d")
# old_files = glob.glob('data/sir_results*.csv')
# for f in old_files:
#     new_loc = 'archive/{}_{}.csv'.format(
#         f.split("/")[-1].split(".")[0],
#         date
#     ) 
#     os.rename(f, new_loc)

# Run model
mod_locs = ['Montana', 'Missoula', 'Gallatin']
for mod_loc in mod_locs:
    print("Running model for " + mod_loc)
    fname = 'sir_results_{}.csv'.format(mod_loc)

    if mod_loc == 'Montana':
        N = 10000
    elif mod_loc == 'Missoula': 
        N = 1000
    elif mod_loc == 'Gallatin':
        N = 1000 

    n_days = 120
    r_0 = 0
    i_0 = 2

    l = SirLearner(data, mod_loc, loss, n_days, r_0, i_0, N)
    beta, gamma, df_mod = l.train()
    print('beta = ' + str(beta))
    print('gamma = ' + str(gamma))
    df_mod['Date'] = df_mod.index
    df_mod.to_csv('data/' + fname)
