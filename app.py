import streamlit as st
from PIL import Image
import pandas as pd
import altair as alt
from datetime import datetime
from libs.obs_utils import *
from libs.sir_utils import *

# Setup title and welcome
now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
st.title('Missoula Covid-19 Dashboard')
st.text('Last update: {}'.format(now))

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

# Model location
# mod_loc = st.sidebar.selectbox(
#     label='Choose location to run SIR model',
#     options=data.columns.to_list(),
# )

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

# Model data
# mod_fname = 'data/sir_results_{}.csv'.format(mod_loc)
# df_mod = pd.read_csv(mod_fname, parse_dates=['Date'])

# df_mod = pd.melt(
#     df_mod, 
#     id_vars='Date', 
#     value_vars=['Actual', 'Susceptible', 'Infectious', 'Recovered'], 
#     value_name='Prediction', 
#     var_name='SIR'
#     )

# st.sidebar.markdown(
#     """
#     [Model details](<https://www.lewuathe.com/covid-19-dynamics-with-sir-model.html>) 
#     """
#     )

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

# Plot model results
# df_mod_sir = df_mod[df_mod['SIR'] != 'Actual']
# df_mod_act = df_mod[df_mod['SIR'] == 'Actual']
# df_mod_act['Points'] = np.repeat('Actual Confirmed', len(df_mod_act))
# chart_sir = (
#     alt.Chart(df_mod_sir)
#     .mark_line()
#     .encode(
#         x = 'Date',
#         y = 'Prediction',
#         color = 'SIR'
#     )
    
# ).interactive()

# chart_actual = (
#     alt.Chart(df_mod_act.dropna())
#     .mark_point(color='black')
#     .encode(
#         x = 'Date', 
#         y = alt.Y('Prediction', title='Population'),
#         shape = 'Points'
#     ).properties(title=mod_loc + ' SIR Model')
# ).interactive()

# chart_mod = alt.layer(chart_sir, chart_actual)

# st.altair_chart(chart_mod, use_container_width=True)

# Bottom text
st.markdown(
    """
    ### Model caveats
    
    I am not an epidemiologist by training, but I enjoy looking at (and trying to understand) data.
    This is an overly simple [SIR model](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology)
    and should be taken with a grain of salt. There are many complexities to the Covid-19
    virus that this model does not account for (e.g. asymptomatic cases). Nonetheless, I hope it is still somewhat
    useful. Please interpret these results wisely.
    
    **I will update the model every day around 5pm with new incoming data.**
    
    ### Important questions to consider (help me answer them):

    1. Are we "flattening the curve" for the state or counties of interest?

        *Right now, it looks like we are. Keep in mind these results are sensitive to our testing biases (which we know are large)
        and we may just be seeing noise in the signal. It is way to early to get overly confident.* 

    2. Have the restrictions had an impact on the curve?

        *Hard to say, but likely yes. Keep on social distancing yourselves, it might just be working!* 
    
    4. Do we want/need this for every county in the state?

        *This app is built to potentially incorporate other counties, but I don't want to spend too much time developing something that is not useful
        to Missoula and the rest of Montana. If the demand is high and people think it is helpful I will happily keep developing. Right
        now I am gauging people's interest.*

    ### A word from the developer
    There is a lot we can do with data. This will be an on going project...I am taking requests for types of 
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

#TODO: Add time to peak, beta, gamma, and HIT interprations for the model results
#TODO: Add uncertainty to parameters