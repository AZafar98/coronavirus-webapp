import pandas as pd
import os
import warnings
import re
from pathlib import Path
from collections import Counter

from src.flask.settings import RUNNING_LOCALLY


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


def get_corona_data():
    """
    Get the data to use for analysis. If it is not saved locally, download it
    :return:
    """
    if RUNNING_LOCALLY:
        file_path = "../../data/json/corona/{}"
    else:
        file_path = "coronavirus-webapp/data/json/corona/{}"

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


confirmed, recovered, deaths = get_corona_data()


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


def data_for_country(data, country, province=None):
    """
    Get the data for specified country and (optional) province.
    :param pd.DataFrame data: COVID data returned from get_corona_data
    :param (str, None) country: Country name. Specify None to return all data.
    :param str province: Province name
    :return: Data for specified country and province
    """

    # Option to return data for all countries
    if country is None:
        country_data = data.copy()
        # We need to remove duplicated countries, otherwise there will be non-unique columns in the index, which causes
        # a problem when convering to JSON. These are countries where the data is split into multiple provinces, so we
        # are simply going to aggregate all of the data
        country_data = aggregate_duplicate_countries(country_data)

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
        total_df = data.loc[:, dates]

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


def display_covid_cases(cases=True, period='Total'):
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
        # return f'{uk_cases:,}'.strip()
        return uk_cases
    else:
        return str(dates)


def covid_time_series(data_type, country=None):
    """

    :param str data_type: 'confirmed', 'deaths' or 'recovered'
    :param (str, None) country: Country to get data for. Default is None which return data for every country.
    :return:
    """

    data_type = data_type.upper()

    if data_type not in ['CONFIRMED', 'DEATHS', 'RECOVERED']:
        raise ValueError("Invalid type. Must be 'confirmed', 'deaths', 'recovered'")

    confirmed, recovered, deaths = get_corona_data()

    if data_type == 'CONFIRMED':
        data = confirmed
    elif data_type == 'DEATHS':
        data = deaths
    else:
        data = recovered

    # This gets UK data by default.
    country_data = data_for_country(data, country, province='None')

    # Get a list of only the date columns
    date_pat = re.compile('\d{1,2}/\d{1,2}/\d{1,2}')
    cols = country_data.columns.tolist()
    date_cols = [col for col in cols if date_pat.match(col)]

    data = country_data[['Country/Region'] + date_cols].T.reset_index()
    data.columns = data.iloc[0].tolist()
    data = data.drop(0, axis=0)
    data = data.rename(columns={'Country/Region': 'Date'})

    return data.to_json()


def country_options():
    # Pass None to get data for all countries back
    country_data = data_for_country(confirmed, None, province='None')

    countries = country_data['Country/Region'].unique().tolist()
    countries = sorted(countries)

    return countries


# test = data_for_country(confirmed, 'United Kingdom', province='None')
test2 = covid_time_series('confirmed', None)

"""
COVID data is updated on GitHub daily. To download it, uncomment the line below. (or delete the existing files saved
locally, but uncommenting the function call below will just overwrite those)
"""

# download_corona_data()
