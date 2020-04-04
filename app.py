import streamlit as st
from PIL import Image
import pandas as pd
import altair as alt
from datetime import datetime
from datetime import timedelta
from libs.obs_utils import *
from libs.sir_utils import *

# Setup title and welcome
st.title('Missoula Covid-19 Dashboard')

# Bring in data
state_names = np.sort(np.load('data/state_names.npy', allow_pickle=True))
# full_data = county_data.append(state_data)
update = state_data.index[-1].strftime("%m/%d/%Y")
st.text('Last update: {}'.format(update))


# Setup sidebar widgets =====================================
# Data location
mt_idx = np.int(np.argwhere(state_names == 'Montana')[0][0])
state_loc = st.sidebar.selectbox(
    label='Choose State',
    options = state_names,
    index=mt_idx
)
state_data = StateCovidData(state=state_loc).cov_update()

county_data = CountyCovidData(state=state_loc).cov_update()
location = st.sidebar.multiselect(
    label='Choose County:',
    options=list(np.sort(county_data['location'].unique())),
    default='Missoula'
)

if not location:
    st.error("Please select at least one location")

if state_loc == 'Montana':
    # Get current numbers
    mt_cases = int(full_data[full_data['location'] == 'Montana'].iloc[-1]['cases'])
    zoo_cases = int(full_data[full_data['location'] == 'Missoula'].iloc[-1]['cases'])



# Calculate difference 
loc_data = full_data.loc[full_data['location'].isin(location)][['location','cases']]
df_loc = loc_data.pivot(columns='location').ffill()['cases']
diff = df_loc.diff()
diff[diff < 0 ] = 0

# This is the forward fill by one day to make the chart look better
# new_index = pd.date_range(df_loc.index.min(), datetime.today() + timedelta(days=1))
# diff = diff.reindex(new_index, method='ffill')

diff['Date'] = diff.index
diff_melt = pd.melt(
    diff, id_vars='Date', 
    value_vars=location, 
    value_name='New Cases', 
    var_name='Location'
    )

# Plot results ============================================
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

# Create checkbox to view dataframe
df_show = df_loc.copy()
df_show.index = df_loc.index.strftime("%Y-%m-%d")
if st.checkbox('Show Covid-19 data'):
    st.write(
        '#### Number of Confirmed Covid-19 Cases:', 
        df_show.sort_index(ascending=False)
        )

# Plot cumulative cases over time
loc_data.columns = ['Location', 'Total Cases']
loc_data['Date'] = loc_data.index
chart = (
    alt.Chart(loc_data)
    .mark_line()
    .encode(
        x='Date',
        y='Total Cases',
        color='Location'
    )
).interactive()

st.altair_chart(chart, use_container_width=True)

chart_diff = (
    alt.Chart(diff_melt)
    .mark_area(
        line=True, 
        opacity=0.4, 
        interpolate='step-after'
    )
    .encode(
        x='Date',
        y=alt.Y('New Cases', stack=False),
        color='Location',
    )
).interactive()

st.altair_chart(chart_diff, use_container_width=True)

# Bottom text
st.markdown(
    """
    ### What's new?

    I added the capability to view data for all Montana counties. You
    can mix and match what you would like to view. I recommend not
    adding too many all at once. Only Montana and Missoula, Lewis and
    Clark, Yellowstone, and Gallatin counties are fully
    up-to-date. The others are about a day or so behind because they
    are based on the New York Times data.

    ### Where'd the model go?

    I am taking the county-level model down for now. I am concerned
    about putting predictions out into the world without them being
    vetted by true experts in the field. I will continue to work on
    the SIR model behind the scenes and would love to team up with
    folks who are interested in developing predictive tools. Feel free
    to contact me by email if you would like to see the model results
    for a specific county or if there are other ways I can help your
    Montana community.

    <nick.covid19@gmail.com>

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

#TODO include all states
#TODO go national
#TODO calculate doubling rate for each county
