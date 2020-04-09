import streamlit as st
from PIL import Image
import pandas as pd
import altair as alt
from datetime import datetime
from datetime import timedelta
from libs.obs_utils import *
from libs.sir_utils import *


# Bring in data and setup sidebar widgets =====================================
# Select state sidebar
state_names = np.sort(np.load('data/state_names.npy', allow_pickle=True))
mt_idx = np.int(np.argwhere(state_names == 'Montana')[0][0])
state_loc = st.sidebar.selectbox(
    label='Choose State',
    options = state_names,
    index=mt_idx
)


# Logic based on location
if state_loc == 'Montana':
    state_data = StateCovidData(state=state_loc).cov_update()
    county_data = CountyCovidData(state=state_loc).cov_update()
    default = 'Missoula'
    mt_cases = int(state_data[state_data['location'] == 'Montana'].iloc[-1]['cases'])
    zoo_cases = int(county_data[county_data['location'] == 'Missoula'].iloc[-1]['cases'])
    np.save('data/current_cases', np.array([mt_cases, zoo_cases]))
else:
    state_data = StateCovidData(state=state_loc).cov_update(update=False)
    county_data = CountyCovidData(state=state_loc).cov_update(update=False)
    default = county_data['location'].iloc[0]
    current_cases = np.load('data/current_cases.npy', allow_pickle=True)
    mt_cases = int(current_cases[0])
    zoo_cases = int(current_cases[1])

# Select county sidebar
location = st.sidebar.multiselect(
    label='Choose County:',
    options=list(np.sort(county_data['location'].unique())),
    default=default
)

if not location:
    st.error("Please select at least one county")

st.sidebar.markdown(
    """
    [View MT Model Comparison](http://mtmodcomp.missoulacov19.com)
    """
)

# Title and update ===============================================================
st.title('Missoula Covid-19 Dashboard')
update = state_data.index[-1].strftime("%m/%d/%Y")
st.text('Last update: {}'.format(update))
st.text("")
st.text("")

# Current status in Montana and Missoula (static)
st.markdown(
    """
    |        | Total Cases |
    |--------|-------------|
    |Montana |{mt_cases}   |
    |Missoula|{zoo_cases}  |
    """.format(
        mt_cases=mt_cases,
        zoo_cases=zoo_cases,
    )
)
st.text("")
st.text("")

# Create one dataframe
county_loc = county_data.loc[county_data['location'].isin(location)][['location','cases']]
county_df_loc = county_loc.pivot(columns='location').ffill()['cases']
state_df_loc = state_data[['location', 'cases']]
state_df_loc = state_df_loc.pivot(columns='location').ffill()['cases']
df_loc = pd.merge(
    state_df_loc, 
    county_df_loc, 
    how='inner', 
    left_index=True, 
    right_index=True
    )

# Melt dataframe
df_melt = df_loc.copy()
df_melt['Date'] = df_melt.index
df_loc_melt = pd.melt(
    df_melt, 
    id_vars='Date', 
    value_vars=location + [state_loc], 
    value_name='Total Cases', 
    var_name='Location'
    )

# Plot results ============================================
# Create checkbox to view dataframe
df_show = df_loc.copy()
df_show.index = df_loc.index.strftime("%Y-%m-%d")
if st.checkbox('Show Covid-19 raw data'):
    st.write(
        '#### Number of Confirmed Covid-19 Cases:', 
        df_show.sort_index(ascending=False)
        )

# Plot cumulative chart
chart = (
    alt.Chart(df_loc_melt)
    .mark_line()
    .encode(
        x='Date',
        y='Total Cases',
        color='Location',
        tooltip=['Date', 'Total Cases']
    )
).interactive()

st.altair_chart(chart, use_container_width=True)

# Plot diff chart

# Calculate difference
if st.checkbox('Show doubling time'):
    df_diff = 0.7/df_loc.pct_change()
    ylab = '# days'
else:
    df_diff = df_loc.diff()
    ylab = 'New Cases'

df_diff[df_diff < 0] = 0
df_diff = df_diff[~df_diff.isin([np.nan, np.inf, -np.inf]).any(1)]
df_diff['Date'] = df_diff.index

# Melt diff dataframe
df_diff_melt = pd.melt(
    df_diff, 
    id_vars='Date', 
    value_vars=location + [state_loc], 
    value_name=ylab, 
    var_name='Location'
    )

chart_diff = (
    alt.Chart(df_diff_melt)
    .mark_area(
        line=True, 
        opacity=0.4, 
        interpolate='step-after'
    )
    .encode(
        x='Date',
        y=alt.Y(ylab, stack=False),
        color='Location',
        tooltip = ['Date', ylab]
    )
).interactive()

st.altair_chart(chart_diff, use_container_width=True)

# Bottom text
st.markdown(
    """
    ### What's new?

    - All states and counties have been added.

    - Added approximate doubling time based on the percent change from the 
    previous day.

    - Can now hover over an area and get the value on both charts.   

    ### Data sources
    [New York Times](<https://github.com/nytimes/covid-19-data>)
    
    [Montana State Library](<https://montana.maps.arcgis.com/apps/MapSeries/index.html?appid=7c34f3412536439491adcc2103421d4b>)
    
    Code for this website is hosted at: <https://github.com/nicksilver/missoula-covid19-website> 
    """
)
st.text("")
st.text("")
st.text("")
# image = Image.open('./static/logo_final_square_trans.png')
image = Image.open('./static/logo_final_text_long_trans.png')
st.image(image, width=200)

#TODO tooltip
