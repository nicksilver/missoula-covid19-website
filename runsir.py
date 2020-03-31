"""
Make sure to run this before deployment
"""

from libs.sir_utils import *
from libs.obs_utils import *
from datetime import datetime
import glob
import os

# Move existing model result data
date = datetime.strftime(datetime.now(), "%Y%m%d")
old_files = glob.glob('data/sir_results*.csv')
for f in old_files:
    new_loc = 'archive/{}_{}.csv'.format(
        f.split("/")[-1].split(".")[0],
        date
    ) 
    os.rename(f, new_loc)

# Bring in data
zoo_data = CovidTrends(county=30063).get_covid_data()
gal_data = CovidTrends(county=30031).get_covid_data()
data = pd.merge(zoo_data, gal_data['Gallatin'], how='inner', left_index=True, right_index=True)

mod_locs = ['Montana', 'Missoula', 'Gallatin']
for mod_loc in mod_locs:
    print("Running model for " + mod_loc)
    fname = 'sir_results_{}.csv'.format(mod_loc)

    if mod_loc == 'Montana':
        N = 10000
    elif mod_loc == 'Missoula' or mod_loc == 'Gallatin':
        N = 1000

    l = SirLearner(data, mod_loc, loss, 90, 0, 2, N)
    beta, gamma, df_mod = l.train()
    df_mod['Date'] = df_mod.index
    df_mod.to_csv('data/' + fname)