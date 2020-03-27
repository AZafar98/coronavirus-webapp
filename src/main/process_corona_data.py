from src.main.corona_data_api_requests import global_timeline, latest, locations, timeline, total
import json
from pprint import pprint
import pandas as pd
import os
import warnings
import re

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



print(confirmed.columns)


def data_for_country(data, country, province = None):
    """
    Get the data for specified country and (optional) province.
    :param pd.DataFrame data: COVID data returned from get_corona_data
    :param str country: Country name. Specify None to return all data.
    :param str province: Province name
    :return: Data for specified country and province
    """

    # Option to return data for all countries
    if country is None:
        country_data = data.copy()
        return country_data.reset_index(drop=True)

    country_data = data.loc[data['Country/Region'].str.upper() == country.upper(),:].reset_index(drop=True)
    if len(country_data) == 0:
        countries = data['Country/Region'].unique().tolist()
        raise ValueError("Invalid country '{}' specified. Available countries are \n {}.".format(country, countries))

    # Some countries have a Python None value for province. Replace these with string so we can still find them
    country_data['Province/State'] = country_data['Province/State'].fillna('None')

    if province is not None:
        provinces = country_data['Province/State'].unique().tolist()
        country_data = country_data.loc[country_data['Province/State'].str.upper() == province.upper(), :]

        # Invalid province specified
        if len(country_data) == 0:
            raise ValueError("Invalid province '{}' specified for country '{}'. Specify province from \n {}."
                             .format(province, country, provinces))

    if len(country_data) > 1:
        provinces = country_data['Province/State'].unique().tolist()
        warnings.warn("More than one province available for {}. Please specify province from {}, or all will be used."
                      .format(country, provinces))

    country_data = country_data.reset_index(drop=True)
    return country_data


def get_latest_figures(data, period='TOTAL'):
    """
    Calculate relevant figures to show to user
    :param pd.DataFrame data:
    :param str period: Either 'Total', '24hrs' or '7days'
    :return:
    """

    # This will assume that the rightmost column contains the most recent data.
    # Note also that the data is aggregated, so total is just given by the rightmost column value
    # TODO: Check date values properly to ensure data is from correct periods

    # Get a list of only the date columns
    date_pat = re.compile('\d{1,2}/\d{1,2}/\d{1,2}')
    cols = data.columns.tolist()
    date_cols = [col for col in cols if date_pat.match(col)]

    if period.upper() == "TOTAL":
        dates = [date_cols[-1]]
        total_df = data.loc[:,dates]

        cases_sum = total_df.sum(axis=0)
        cases = cases_sum.iat[0]

        # Also return the dates the data is from so we can display this
        return cases, date_cols[-1]

    if period.upper() == '24H':
        # Now need to calculate the difference between the two most recent data points
        dates = date_cols[-2:]
        total_df = data.loc[:, dates]

        # New cases in the period is just the difference between the first and last columns since the data is aggregated
        new_cases_df = total_df.iloc[:, -1] - total_df.iloc[:, 0]

        new_cases_sum = new_cases_df.sum(axis=0)

        dates_used = ' - '.join([date_cols[-2], date_cols[-1]])

        # Also return the dates the data is from so we can display this
        return new_cases_sum, dates_used

    if period.upper() == '7DAYS':
        # Now need to calculate the difference between the two most recent data points
        dates = date_cols[-7:]
        total_df = data.loc[:, dates]

        # New cases in the period is just the difference between the first and last columns since the data is aggregated
        new_cases_df = total_df.iloc[:, -1] - total_df.iloc[:, 0]

        new_cases_sum = new_cases_df.sum(axis=0)

        dates_used = ' - '.join([date_cols[-7], date_cols[-1]])

        # Also return the dates the data is from so we can display this
        return new_cases_sum, dates_used


def display_covid_cases(cases = True, period = 'Total'):
    """

    :param bool cases: If True, return number of cases in period. If False, return dates used for that period.
    :param period: Currently either Total, 24H or 7Days
    :return:
    """

    period = period.upper()

    # For now, this is set up to use UK data only. Need to figure out Flask a bit better to pass parameters down.
    uk_data = data_for_country(confirmed, 'United Kingdom', province='None')

    if period not in ['TOTAL', '24H', '7DAYS']:
        raise ValueError("Invalid time period. Must be either 'TOTAL', '24H', or '7DAYS'")

    uk_cases, dates = get_latest_figures(uk_data, period=period)

    if cases is True:
        return uk_cases
    else:
        return dates

