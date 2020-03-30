import streamlit as st
import pandas as pd
import altair as alt
from libs.county_utils import *

# Setup title and welcome
st.title('Missoula COVID19 Dashboard')
st.text('Welcome to the Missoula COVID19 Dashboard')

# Bring in data for Montana and Missoula
data = CovidTrends(county=30063).get_covid_data()

# Create checkbox to view dataframe
if st.checkbox('Show dataframe'):
    st.write('#### Number of Confirmed COVID19 Cases:', data)

# Melt data frame
df = data.copy()
df['Date'] = df.index
df_melt = pd.melt(
    df, id_vars='Date', 
    value_vars=['Montana', 'Missoula'], 
    value_name='Cases', 
    var_name='Location'
    )

# Plot cumulative cases over time
chart = (
    alt.Chart(df_melt)
    .mark_line()
    .encode(
        x='Date',
        y='Cases',
        color='Location'
    )
).interactive()

st.altair_chart(chart, use_container_width=True)

# Calculate difference and melt dataframe
diff = data.diff()
diff['Date'] = diff.index
diff_melt = pd.melt(
    diff, id_vars='Date', 
    value_vars=['Montana', 'Missoula'], 
    value_name='New Cases', 
    var_name='Location'
    )

# Plot epidemic curve
chart_diff = (
    alt.Chart(diff_melt)
    .mark_bar(opacity=0.7, width=25)
    .encode(
        x='Date',
        y=alt.Y('New Cases', stack=None),
        color='Location',
    )
).interactive()

st.altair_chart(chart_diff, use_container_width=True)

