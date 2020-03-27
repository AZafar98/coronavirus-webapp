from src.main.corona_data_api_requests import global_timeline, latest, locations, timeline, total
import json
from pprint import pprint
import pandas as pd
import os

# We need to do some stuff with the data returned by the API calls to display the relevant info

# Since we probably don't want to call the API every time the page is loaded, save the latest data locally and
# read from that instead

GET_DATA = False

def write_json(in_json, filename):
    """
    Utility function to write the data to a text file in JSON format.
    :param in_json: Data returned from API call to be written
    :param filename: Filename, including (.txt) extension
    :return: 0
    """

    json_path = "../../data/json/{}"

    # Load the string data into a dict using JSON Loads so it will be read back in as a dict and not a string
    out_json = json.loads(in_json)

    with open(json_path.format(filename), 'w') as outfile:
        json.dump(out_json, outfile)

    return 0

def save_corona_data():
    """
    Send API requests and save JSON locally
    :return:
    """

    global_timeline_json = global_timeline()
    latest_json = latest()
    locations_json = locations()
    timelines_json = timeline('GB')
    total_json = total('GB')

    write_json(global_timeline_json, "global_timeline_json.txt")
    write_json(latest_json, "latest_json.txt")
    write_json(locations_json, "locations_json.txt")
    write_json(timelines_json, "timelines_json.txt")
    write_json(total_json, "total_json.txt")

    return 0

# GET_DATA=True
if GET_DATA is True:
    save_corona_data()


def get_cases_from_json():
    with open('../../data/json/locations_json.txt') as json_file:
        data = json.load(json_file)

        # JSON is read into a dictionary which has a bunch of other dictionaries in it. Extract the UK data from the dict.

        for data_dict in data['locations']:
        # Province is excluded so we just get UK data, not territories like Gibraltar too, for example
            if data_dict['country'].upper().strip() == 'UNITED KINGDOM' and data_dict[
                'province'].upper().strip() == 'UNITED KINGDOM':

                case_data = data_dict['latest']
                confirmed, deaths, latest = map(case_data.get, ('confirmed', 'deaths', 'recovered'))

                break

    # TODO: For simplicity, just return confirmed cases for now. Might be useful to return other data later.
    # return confirmed, deaths, latest
    return f'{confirmed:,}'.strip()


def download_corona_data():
    """
    Get the data straight from the Git repo, since the API has stopped working

    The data is updated once per day, so this function should be run daily.
    :return:
    """

    OUT_PATH = "../../data/json/{}"

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

# download_corona_data()

def get_corona_data():
    """
    Get the data to use for analysis. If it is not saved locally, download it
    :return:
    """

    if not (os.path.exists("../../data/json/confirmed_cases.txt") or
            os.path.exists("../../data/json/deaths_cases.txt") or
            os.path.exists("../../data/json/recovered_cases.txt")):

        print("error")
        download_corona_data()

    else:
        confirmed_df = pd.read_json("../../data/json/confirmed_cases.txt")
        recovered_df = pd.read_json("../../data/json/recovered_cases.txt")
        deaths_df = pd.read_json("../../data/json/deaths_cases.txt")

    return confirmed_df, recovered_df, deaths_df

confirmed, recovered, deaths = get_corona_data()

