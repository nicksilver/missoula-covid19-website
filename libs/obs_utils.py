import pandas as pd
import numpy as np

nyt_county = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
nyt_state = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
usa_facts = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'
mt_data = 'https://www.arcgis.com/sharing/rest/content/items/0d47920e54e0420cb604213acc8761d5/data'
nls_mt_data = './data/mt_covid19_update.csv'

class CountyCovidData(object):
    """
    Merges NYT county data with updated MSL data and returns dataframe
    """

    def __init__(self, state='Montana'):
        self.state=state

    def get_nyt_data(self):
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
        nyt_data = nyt_data[nyt_data['state'] == self.state]
        nyt_data['source'] = np.repeat('nyt', len(nyt_data)) 
        return nyt_data
    
    def get_msl_data(self):
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
        return mt_melt
    
    def merge_data(self, nyt_data, msl_data):
        
        df_full = pd.merge(
            nyt_data, 
            msl_data, 
            how='outer',
            on=['county', 'cases', 'source'],
            right_index=True,
            left_index=True 
            )
        df_full = df_full[['county', 'cases', 'deaths', 'source']]
        df_full.ffill(axis=0, inplace=True)
        df_full.bfill(axis=0, inplace=True)
        df_full.rename(columns={'county':'location'}, inplace=True)
        df_full = df_full.groupby([df_full.index, 'location']).first().reset_index(['location'])
        return df_full

    def cov_update(self, update=True):

        nyt_data = self.get_nyt_data()
        if update:
            msl_data = self.get_msl_data()
            full_data = self.merge_data(nyt_data, msl_data)
        else:
            full_data = nyt_data.copy()
            full_data = full_data[['county', 'cases', 'deaths', 'source']]
            full_data.rename(columns={'county':'location'}, inplace=True)
        return full_data

class StateCovidData(object):
    """
    Merges NYT state data with updated MSL data and returns dataframe
    """
    def __init__(self, state='Montana'):
        self.state = state

    def get_nyt_data(self):

        datatypes = {
            'date': 'str',
            'county': 'str',
            'state': 'str',
            'fips': 'Int64',
            'cases': 'float',
            'deaths': 'float'
                }

        nyt_data = pd.read_csv(nyt_state, dtype=datatypes, parse_dates=[0])
        nyt_data.set_index('date',  inplace=True)
        nyt_data = nyt_data[nyt_data['state'] == self.state]
        nyt_data['source'] = np.repeat('nyt', len(nyt_data)) 
        return nyt_data

    def get_msl_data(self):
        mt_data = pd.read_csv("./data/mt_covid19_update.csv")
        mt_data.set_index('date', inplace=True)
        locations = ['Montana']
        mt_data['date'] = pd.to_datetime(mt_data.index)
        mt_melt = pd.melt(
            mt_data, 
            id_vars='date', 
            value_vars=locations, 
            value_name='cases', 
            var_name='state'
            )
        mt_melt['source'] = np.repeat('msl', len(mt_melt))
        mt_melt.set_index('date', inplace=True)
        return mt_melt

    def merge_data(self, nyt_data, msl_data):
        df_full = pd.merge(
            nyt_data, 
            msl_data, 
            how='outer',
            on=['state', 'cases', 'source'],
            right_index=True,
            left_index=True 
            )
        df_full = df_full[['state', 'cases', 'deaths', 'source']]
        df_full.ffill(axis=0, inplace=True)
        df_full.bfill(axis=0, inplace=True)
        df_full.rename(columns={'state':'location'}, inplace=True)
        return df_full

    def cov_update(self, update=True):

        nyt_data = self.get_nyt_data()
        if update:
            msl_data = self.get_msl_data()
            full_data = self.merge_data(nyt_data, msl_data)
        else:
            full_data = nyt_data.copy()
            full_data = full_data[['state', 'cases', 'deaths', 'source']]
            full_data.rename(columns={'state':'location'}, inplace=True)
        return full_data

    

    
    
StateCovidData().cov_update()

class CovidTrends(object):
    
    def __init__(self, state='Montana', county=None):
        self.state = state
        self.county = county
        self.state_df = self.get_nyt_state_data()
        if county and county != 'ALL':
            self.county_name = self.state_df[self.state_df['fips'] == self.county]['county'][0]

    def get_nyt_state_data(self):

        datatypes = {
            'date': 'str',
            'state': 'str',
            'fips': 'Int64',
            'cases': 'Int64',
            'deaths': 'Int64'
        }

        nyt_df = pd.read_csv(nyt_county, dtype=datatypes, parse_dates=[0])
        nyt_df.set_index('date',  inplace=True)

        return nyt_df[nyt_df['state'] == self.state]

    def select_county_data(self):
        county_df_all = self.state_df[self.state_df['fips'] == self.county]
        county_df = county_df_all['cases'].to_frame()
        county_df.columns = [self.county]
        return county_df

    def fill_mt_state_data(self, state_df_grp):
        nls_df = pd.read_csv(nls_mt_data, parse_dates=[0], index_col=['date'])
        state_fill_df = pd.merge(state_df_grp, nls_df['Montana'], how='outer', 
            left_index=True, right_index=True)
        return state_fill_df[self.state].fillna(nls_df['Montana']).to_frame()
  
    def fill_county_data(self, county_df):
        nls_df = pd.read_csv(nls_mt_data, parse_dates=[0], index_col=['date'])
        county_df = pd.merge(county_df[self.county], nls_df[self.county_name], how='outer', 
            left_index=True, right_index=True)
        return county_df[self.county].fillna(county_df[self.county_name]).to_frame()

    def get_covid_data(self):

        state_df_grp = self.state_df.groupby('date').sum()[['cases']]
        state_df_grp.columns = [self.state]

        if self.state == 'Montana':
            state_fill_df = self.fill_mt_state_data(state_df_grp)
            df = state_fill_df

            if self.county:
                county_df = self.select_county_data()

                if self.county == 'ALL':
                    self.fill_county_data(county_df)

                if self.county == 30063 or self.county == 30031:
                    county_df = self.fill_county_data(county_df)

                df = pd.merge(state_fill_df, county_df, how='outer', right_index=True, left_index=True)
                df.columns = [self.state, self.county_name]

        else:

            df = state_df_grp

            if self.county:
                county_df_all = self.select_county_data()
                df = pd.merge(state_df_grp, county_df, how='outer', right_index=True, left_index=True)
                df.columns = [self.state, self.county_name]
        
        return df 

# CovidTrends(county=30063).get_covid_data()