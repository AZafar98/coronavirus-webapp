import pandas as pd
from pathlib import Path
import os
import sys
import re

# add your project directory to the sys.path.
# This is purely for PythonAnywhere - not necessary if running locally
project_home = '/home/Azafar98/coronavirus-webapp'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from src.flask.settings import RUNNING_LOCALLY


# This is to redeploy the webapp after the data has been downloaded.
def update():
    os.utime('/var/www/azafar98_pythonanywhere_com_wsgi.py')


def download_corona_data():
    """
    Get the data straight from the Git repo, since the API has stopped working

    The data is updated once per day, so this function should be run daily.
    :return:
    """

    # Make sure the required path exists. Create it if not.
    # On PythonAnywhere, the paths are a bit different.
    try:
        Path("../../data/json/corona").mkdir(parents=True, exist_ok=True)
        OUT_PATH = "../../data/json/corona/{}"
    except PermissionError:
        Path("coronavirus-webapp/data/json/corona").mkdir(parents=True, exist_ok=True)
        OUT_PATH = "coronavirus-webapp/data/json/corona/{}"

    CONFIRMED_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    DEATHS_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    RECOVERED_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"


    confirmed_data = pd.read_csv(CONFIRMED_URL)
    deaths_data = pd.read_csv(DEATHS_URL)
    recovered_data = pd.read_csv(RECOVERED_URL)

    # Save the data locally so it doesn't have to be accessed from GitHub every time.
    confirmed_data.to_json(OUT_PATH.format("confirmed_cases.txt"))
    deaths_data.to_json(OUT_PATH.format("deaths_cases.txt"))
    recovered_data.to_json(OUT_PATH.format("recovered_cases.txt"))

    return 0


if not RUNNING_LOCALLY:
    download = download_corona_data()
    if download == 0:
        update()
else:
    download_corona_data()
