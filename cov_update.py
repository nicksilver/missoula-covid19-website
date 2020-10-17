import pandas as pd
import numpy as np

def cov_update(state='Montana'):
    nyt_county = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

    datatypes = {
        'date': 'str',
        'county': 'str',
        'state': 'str',
        'fips': 'Int64',
        'cases': 'float',
        'deaths': 'float'
            }

    nyt_data = pd.read_csv(nyt_county, dtype=datatypes, parse_dates=[0])
    nyt_data.set_index('date',  inplace=True)
    nyt_data = nyt_data[nyt_data['state'] == state]
    nyt_data['source'] = np.repeat('nyt', len(nyt_data)) 

    mt_data = pd.read_csv("./data/mt_covid19_update.csv")
    mt_data.set_index('date', inplace=True)
    locations = ['Missoula', 'Gallatin', 'Yellowstone', 'Lewis and Clark']
    mt_data['date'] = pd.to_datetime(mt_data.index)
    mt_melt = pd.melt(
        mt_data, 
        id_vars='date', 
        value_vars=locations, 
        value_name='cases', 
        var_name='county'
        )
    mt_melt['source'] = np.repeat('msl', len(mt_melt))
    mt_melt.set_index('date', inplace=True)
    df_full = pd.merge(
        nyt_data, 
        mt_melt, 
        how='outer',
        on=['county', 'cases', 'source'],
        right_index=True,
        left_index=True 
        )
    df_full = df_full[['county', 'cases', 'deaths', 'source']]
    df_full.ffill(axis=0, inplace=True)
    df_full.bfill(axis=0, inplace=True)
    df_full.to_csv('./data/mt_covid19_data_all.csv')

if __name__=='__main__':
    cov_update()