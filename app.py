import streamlit as st
from PIL import Image
import pandas as pd
import altair as alt
from datetime import datetime
from datetime import timedelta
from libs.obs_utils import *
from libs.sir_utils import *
from libs.gsheet import *
import os
import json

# Google Sheets credentials
SPREADSHEET_ID = "1ZHnIEjpFZ9U9Iu5VJfdTVKU2NiVBMtrvjDekRKsXmLs"
SCOPE = ['https://www.googleapis.com/auth/spreadsheets',]
GOOGLE_CREDS = "google-credentials.json"

# GOOGLE_CREDS = json.loads(os.getenv('GOOGLE_CREDENTIALS')) 


# Bring in Google Sheets data
gs_df = gsheet2df(SPREADSHEET_ID, GOOGLE_CREDS, SCOPE, debug=True)
update = gs_df.Date.iloc[-1]
mt_cases = gs_df['Active infected'].iloc[-1]
zoo_cases = gs_df['Active Missoula'].iloc[-1]

# Title
st.title('Missoula Covid-19 Dashboard')
st.text('Last update: {}'.format(update))
st.markdown(
    """
    The State has put together a very nice [Montana Covid-19 Dashboard](https://montana.maps.arcgis.com/apps/MapSeries/index.html?appid=7c34f3412536439491adcc2103421d4b)
    but it focuses on the geographic spread of the virus. This dashboard shows how things are changing over time. I built this mainly for me to keep track of things, but maybe others
    will find it helpful.
    """
)
st.text("")
st.text("")

# Current active status in Montana and Missoula (static)
st.markdown(
    """
    |        | Total Active Cases |
    |--------|--------------------|
    |Montana |{mt_cases}          |
    |Missoula|{zoo_cases}         |
    """.format(
        mt_cases=mt_cases,
        zoo_cases=zoo_cases,
    )
)
st.text("")
st.text("")

# Format Gsheet data
gs_df.Date = pd.to_datetime(gs_df.Date)
gs_df.set_index('Date', inplace=True)
gs_df.replace("", np.nan, inplace=True)
active_df = gs_df[['Active infected', 'Active Missoula']]
active_df.columns = ['Montana', 'Missoula']
active_df = active_df.dropna(axis=0, how='all')
testing_df = pd.DataFrame(gs_df['Tests completed'])
testing_df.columns = ['Tests Completed']

# Plot active cases
zoo_pop = 120000
mt_pop = 1069000

# Create dataframe with CDC indicators
cdc_df = pd.DataFrame({
    '14day New Cases': [float(gs_df['Missoula New Cases'].iloc[-1])],
    '14day % Change': [float(gs_df['Missoula % Change'].iloc[-1])],
    '7day Pos. Rate': [float(gs_df['Missoula Positivity Rate'].iloc[-1])]
    # 'Hosp. % Full': [float(gs_df['Missoula Hosp. % Full'].iloc[-1])],
    # 'Hosp. % COV19': [float(gs_df['Missoula Cov. Hosp. %'].iloc[-1])]
})

st.markdown(
    """
    ### CDC Indicators for Transmission of COVID-19 in Missoula Schools

    Below are some of the values the CDC recommends for schools to use to determine risk
    of transmission. They are calculated for Missoula County. 
    
    Click [here](https://www.cdc.gov/coronavirus/2019-ncov/downloads/community/schools-childcare/indicators-thresholds-table.pdf)
    for CDC details on the indicators and color coding. 
    
    **TL;DR** => green(ish) is good; red(ish) is bad. 

    """
)

st.table(cdc_df.style.apply(add_color_style, axis=1))

st.markdown(
    """
    _**Positivity Rate**_ is updated every week or so and is based on a 7-day average rather than the CDC 
    recommended 14-day average. 
    """
)


st.markdown(
    """
    ### Active Cases
    The number of active cases of Covid-19 in Montana (orange) and Missoula (blue). 
    To get exact numbers select the checkbox below or zoom and hover on the chart.
    """
)

active_df['Missoula'] = pd.to_numeric(active_df.loc[:, 'Missoula'])
active_df['Montana'] = pd.to_numeric(active_df.loc[:, 'Montana'])
active_df.index = active_df.index.strftime("%Y-%m-%d")
if st.checkbox('Show Data Normalized by Population'):
    active_df['Missoula'] = 100000*(active_df.loc[:, 'Missoula']/zoo_pop)
    active_df['Montana'] = 100000*(active_df.loc[:, 'Montana']/mt_pop)
    active_lab = 'Active Cases / 100k People'
else:
    active_lab = 'Active Cases'

if st.checkbox('Show Raw Data For Active Cases'):
    st.write(
        '#### Active cases:', 
        active_df.sort_index(ascending=False)
        )

# Plot active cases
active_df['Date'] = pd.to_datetime(active_df.index)
active_melt = pd.melt(
    active_df,
    id_vars='Date',
    var_name = 'Location',
    value_name= active_lab
)

active_chart = (
    alt.Chart(active_melt)
    .mark_line()
    .encode(
        x='Date',
        y=active_lab,
        color='Location',
        tooltip=['Date', active_lab]
    )
).interactive()

st.altair_chart(active_chart, use_container_width=True)

# Plot testing data
st.markdown(
    """
    ### Daily Covid-19 Tests Completed in Montana
    The number of daily Covid-19 tests administered in Montana.
    To get exact numbers select the checkbox below or zoom and hover on the chart.
    """
)


testing_df.index = testing_df.index.strftime("%Y-%m-%d")
if st.checkbox('Show Raw Data For Daily Tests Completed'):
    st.write(
        '#### Tests Completed:', 
        testing_df.sort_index(ascending=False)
        )


testing_df['Date'] = pd.to_datetime(testing_df.index)
testing_df['Tests Completed'] = pd.to_numeric(testing_df.loc[:,'Tests Completed'])

testing_chart = (
    alt.Chart(testing_df)
    .mark_area(
        line=True, 
        opacity=0.4, 
        interpolate='step-after'
    )
    .encode(
        x='Date',
        y='Tests Completed',
        tooltip = ['Date', 'Tests Completed']
    )
).interactive()
st.altair_chart(testing_chart, use_container_width=True)

# Select state 
st.markdown(
    """
    ### Explore Data From Other Counties
    In the section below you can select other States and Counties to explore their total 
    confirmed cases, daily confirmed cases, and doubling time (use the checkbox in the second chart). 
    To get exact numbers select the checkbox for total confirmed cases or zoom and hover on the chart.
    """
)

state_names = np.sort(np.load('data/state_names.npy', allow_pickle=True))
mt_idx = np.int(np.argwhere(state_names == 'Montana')[0][0])
state_loc = st.selectbox(
    label='Choose State:',
    options = state_names,
    index=mt_idx
)

state_data = StateCovidData(state=state_loc).cov_update(update=False)
county_data = CountyCovidData(state=state_loc).cov_update(update=False)

if state_loc == 'Montana':    
    default = 'Missoula'
else:
    default = county_data['location'].iloc[0]

# Select county 
location = st.multiselect(
    label='Choose County:',
    options=list(np.sort(county_data['location'].unique())),
    default=default
)

if not location:
    st.error("Please select at least one county")

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

# Select start date
month_list = df_loc.index.strftime('%B').unique()
start_month = st.selectbox(
    label = 'Choose Start Month:',
    options = list(month_list),
)
start_date = datetime.strptime(start_month + ' 2020', '%B %Y')
df_loc = df_loc.loc[df_loc.index > start_date]

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
if st.checkbox('Show Raw Data For Total Confirmed Cases'):
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
    - Added some of the CDC indicators for schools (10/17/2020)
    
    - Added 'start month' selection (7/08/2020)

    - Normalized MT active cases by population (6/29/2020)

    - New layout with Missoula specific charts added (6/25/2020)

    ### Data sources
    [Montana State Library](<https://montana.maps.arcgis.com/apps/MapSeries/index.html?appid=7c34f3412536439491adcc2103421d4b>)
    
    [CDC COVID-19 School Indicators](<https://www.cdc.gov/coronavirus/2019-ncov/community/schools-childcare/indicators.html#thresholds>)

    [MCPS COVID-19 Advisory](<https://www.mcpsmt.org/COVID-19>)

    [MT DPHHS COVID-19 Advisory](<https://dphhs.mt.gov/publichealth/cdepi/diseases/coronavirusmt>)

    [New York Times](<https://github.com/nytimes/covid-19-data>)
    
    Code for this website is hosted at: <https://github.com/nicksilver/missoula-covid19-website> 
    """
)
st.text("")
st.text("")
st.text("")
# image = Image.open('./static/logo_final_square_trans.png')
image = Image.open('./static/logo_final_text_long_trans.png')
st.image(image, width=200)
