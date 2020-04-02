# Missoula/Montana Covid-19 Website

www.missoulacovid19.com

### Dependencies

- Python 3.7.3
- scipy
- pandas
- numpy
- streamlit
- altair

see `requirements.txt` for versions

### Data sources

[New York Times](<https://github.com/nytimes/covid-19-data>)

[Montana State Library](<https://montana.maps.arcgis.com/apps/MapSeries/index.html?appid=7c34f3412536439491adcc2103421d4b>)

### Manual labor

In order to get this app running quickly I have not fully automated everything, therefore, it takes a bit of manual labor to update. Here are the current steps I take:

1) At 4:30 pm the State updates the daily Covid-19 case totals. I add these values to the `/data/mt_coronavirus_status.csv` file. This file is only used for the latest data because the NYT data seems to lag by 2 days.

2) I then run the `runsir.py` file locally which runs the SIR model and saves the results in `.csv` files. It also archives old model results locally so that we can look back at our predictions at a later date. 

3) I spend a bit of time tuning the model to make sure we get realistic solutions. Because it is still early and the signal is not strong (especially in Missoula) you can get some funky results. 

4) Once I like the model, I run `runsir.py` one more time to save the preferred model results to the repository.

5) Commit the changes.

6) Push to [Heroku](www.heroku.com)

### The model

Currently, I am using N=10000 for Montana and N=1000 for Missoula and Gallatin counties. Betas and gammas will be reported on the website in future versions. 

The code was adapted (hijacked) from the great work of [Lewauathe](https://github.com/Lewuathe/COVID19-SIR/blob/master/solver.py) and their [blog post](https://www.lewuathe.com/covid-19-dynamics-with-sir-model.html). Thank you!

### TODOS

- Add uncertainty to the model
- Report and interpret peak timing, peak magnitude, beta, gamma, R_0 and HIT from the model results.
- Add previous model runs
- Add other (all) counties in Montana
- Improve model: [Li et al. 2020](https://science.sciencemag.org/content/early/2020/03/24/science.abb3221/tab-pdf)