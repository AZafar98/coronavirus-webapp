import pandas as pd
from pathlib import Path
import os
import sys
import re
from collections import Counter

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


def aggregate_duplicate_countries(data):
    countries = data['Country/Region'].tolist()
    count_countries = Counter(countries)
    duplicates = [country for country, count in count_countries.items() if count > 1]

    for duplicate_country in duplicates:
        temp_data = data.loc[data['Country/Region'] == duplicate_country, :]
        temp_data = temp_data.sum(axis=0)
        temp_data['Province/State'] = 'None'
        temp_data['Country/Region'] = duplicate_country

        # Drop all of the old data before inserting the aggregated data
        data = data.loc[data['Country/Region'] != duplicate_country, :]

        temp_data = temp_data.to_frame().T
        data = pd.concat([data, temp_data], axis=0)

    return data


def get_corona_data():
    """
    Get the data to use for analysis. If it is not saved locally, download it
    :return:
    """
    if RUNNING_LOCALLY:
        file_path = "../../data/json/corona/{}"
    else:
        file_path = "/home/Azafar98/coronavirus-webapp/data/json/corona/{}"

    if not (os.path.exists(file_path.format("confirmed_cases.txt")) or
            os.path.exists(file_path.format("deaths_cases.txt")) or
            os.path.exists(file_path.format("recovered_cases.txt"))):

        print("corona data not downloaded. Downloading.")

        download = download_corona_data()

        if download == 0:
            # Successful download.
            confirmed_df = pd.read_json(file_path.format("confirmed_cases.txt"))
            recovered_df = pd.read_json(file_path.format("recovered_cases.txt"))
            deaths_df = pd.read_json(file_path.format("deaths_cases.txt"))
        else:
            # Download failed
            raise RuntimeError("Data failed to download. Exiting process.")

    else:
        confirmed_df = pd.read_json(file_path.format("confirmed_cases.txt"))
        recovered_df = pd.read_json(file_path.format("recovered_cases.txt"))
        deaths_df = pd.read_json(file_path.format("deaths_cases.txt"))

    return confirmed_df, recovered_df, deaths_df


def update_covid_time_series(data_type):

    confirmed, recovered, deaths = get_corona_data()

    data_type = data_type.upper()

    if data_type == 'CONFIRMED':
        data = confirmed
    elif data_type == 'DEATHS':
        data = deaths
    else:
        data = recovered

    country_data = aggregate_duplicate_countries(data).reset_index(drop=True)

    # Get a list of only the date columns
    date_pat = re.compile('\d{1,2}/\d{1,2}/\d{1,2}')
    cols = country_data.columns.tolist()
    date_cols = [col for col in cols if date_pat.match(col)]

    data = country_data[['Country/Region'] + date_cols].T.reset_index()
    data.columns = data.iloc[0].tolist()
    data = data.drop(0, axis=0)
    data = data.rename(columns={'Country/Region': 'Date'}).reset_index(drop=True)

    data_to_difference = data.loc[:, [col for col in data.columns if col != 'Date']]
    differenced = data_to_difference.diff()
    # First row will be NA values after differencing. Drop that so it doesn't cause problems later when trying to
    # graph the data
    differenced['Date'] = data['Date']
    differenced = differenced.drop(1, axis=0).reset_index(drop=True)

    if RUNNING_LOCALLY:
        file_path = "../../data/json/corona/{}"
    else:
        file_path = "coronavirus-webapp/data/json/corona/{}"

    data.to_json(file_path.format("{}-covid-time-series.txt").format(data_type.lower()))
    differenced.to_json(file_path.format("{}-covid-time-series-diff.txt").format(data_type.lower()))

    return 0


if not RUNNING_LOCALLY:
    download = download_corona_data()
    update_covid_time_series('confirmed')
    update_covid_time_series('deaths')
    update_covid_time_series('recovered')

    if download == 0:
        update()
else:
    download_corona_data()
    update_covid_time_series('confirmed')
    update_covid_time_series('deaths')
    update_covid_time_series('recovered')
