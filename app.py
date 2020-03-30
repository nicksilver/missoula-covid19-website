import streamlit as st
from PIL import Image
import pandas as pd
import altair as alt
from datetime import datetime
from libs.county_utils import *

# Setup title and welcome
now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
st.title('Missoula Covid-19 Dashboard')
st.text('Last update: {}'.format(now))

# Bring in data for Montana and Missoula
zoo_data = CovidTrends(county=30063).get_covid_data()
gal_data = CovidTrends(county=30031).get_covid_data()
data = pd.merge(zoo_data, gal_data['Gallatin'], how='inner', left_index=True, right_index=True)


# Get current numbers
mt_cases = data['Montana'].iloc[-1]
zoo_cases = data['Missoula'].iloc[-1]

st.markdown(
    """
    |        | Total Cases |
    |--------|-------------|
    |Montana |{mt_cases}   |
    |Missoula|{zoo_cases}  |
    """.format(
        mt_cases=mt_cases,
        zoo_cases=zoo_cases
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

# Melt data frame
df = data.copy()
df['Date'] = df.index
df_melt = pd.melt(
    df, id_vars='Date', 
    value_vars=['Montana', 'Missoula', 'Gallatin'], 
    value_name='Total Cases', 
    var_name='Location'
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

# Calculate difference and melt dataframe
diff = data.diff()
diff['Date'] = diff.index
diff_melt = pd.melt(
    diff, id_vars='Date', 
    value_vars=['Montana', 'Missoula', 'Gallatin'], 
    value_name='New Cases', 
    var_name='Location'
    )

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

st.markdown(
    """
    To understand where we are, we have to know where we've been. 
    This dashboard shows trends in Covid-19 for Montana and Missoula 
    since our first cases were confirmed in early March. 
    
    There is a lot we can do with data. This will be an on going project...
    so check back frequently for updates. I am taking requests for types of 
    data to visualize and models to build for the community. 

    Please feel free to reach out if there are ways I can help: 
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
st.image(image, width=200, )