import pandas as pd
import os
import warnings
import re
from pathlib import Path

def download_corona_data():
    """
    Get the data straight from the Git repo, since the API has stopped working

    The data is updated once per day, so this function should be run daily.
    :return:
    """

    # Make sure the required path exists. Create it if not.
    Path("../../data/json/corona").mkdir(parents=True, exist_ok=True)

    OUT_PATH = "../../data/json/corona/{}"

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

# download_corona_data()


def get_corona_data():
    """
    Get the data to use for analysis. If it is not saved locally, download it
    :return:
    """

    file_path = "../../data/json/corona/{}"

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
