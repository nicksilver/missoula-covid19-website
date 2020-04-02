import streamlit as st
from PIL import Image
import pandas as pd
import altair as alt
from datetime import datetime
from libs.obs_utils import *
from libs.sir_utils import *

# Setup title and welcome
st.title('Missoula Covid-19 Dashboard')

# Bring in data
zoo_data = CovidTrends(county=30063).get_covid_data()
gal_data = CovidTrends(county=30031).get_covid_data()
data = pd.merge(
    zoo_data, 
    gal_data['Gallatin'], 
    how='inner', 
    left_index=True, 
    right_index=True
    )
update = data.index[-1].strftime("%m/%d/%Y")
st.text('Last update: {}'.format(update))

# Get current numbers
mt_cases = data['Montana'].iloc[-1]
zoo_cases = data['Missoula'].iloc[-1]
gal_cases = data['Gallatin'].iloc[-1]

# Setup sidebar widgets =====================================
# Data location
location = st.sidebar.multiselect(
    label='Choose location to view data:',
    options=data.columns.to_list(),
    default=['Montana', 'Missoula']
)

if not location:
    st.error("Please select at least one location")

# Data processing ============================================
# Melt data frame
loc_data = data[location]
df = loc_data.copy()
df['Date'] = df.index
df_melt = pd.melt(
    df, id_vars='Date', 
    value_vars=location, 
    value_name='Total Cases', 
    var_name='Location'
    )

# Calculate difference and melt dataframe
diff = loc_data.diff()
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
    |Gallatin|{gal_cases}  |
    """.format(
        mt_cases=mt_cases,
        zoo_cases=zoo_cases,
        gal_cases=gal_cases
    )
)
st.text("")
st.text("")

# Create checkbox to view dataframe
if st.checkbox('Show Covid-19 data'):
    st.write(
        '#### Number of Confirmed Covid-19 Cases:', 
        data.sort_index(ascending=False)
        )

# Plot cumulative cases over time
chart = (
    alt.Chart(df_melt)
    .mark_line()
    .encode(
        x='Date',
        y='Total Cases',
        color='Location'
    )
).interactive()

st.altair_chart(chart, use_container_width=True)

# Plot epidemic curve
chart_diff = (
    alt.Chart(diff_melt)
    .mark_bar(width=20, opacity=0.4)
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
    ### Where'd the model go?

    I am taking the county-level model down for now. I am concerned about putting predictions out into the world without 
    them being vetted by true experts in the field. I will continue to work on the SIR model behind the scenes
    and would love to team up with folks who are interested in developing predictive tools. Feel free to contact me by email if 
    you would like to see the model results for a specific county or if there are other ways I can help your Montana community.   

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

#TODO: look into alt.Chart(source).mark_area(
#     color="lightblue",
#     interpolate='step-after',
#     line=True
# ).encode(
#     x='date',
#     y='price'
# ).transform_filter(alt.datum.symbol == 'GOOG')