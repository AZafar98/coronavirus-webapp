import pandas as pd
import os
import warnings
import re
from pathlib import Path
from collections import Counter
import json


def set_env():
    curr_wd = os.getcwd()
    if 'dev' in curr_wd:
        ENV = 'DEV'
    elif 'prod' in curr_wd:
        ENV = 'PROD'
    else:
        ENV = None
    return ENV


ENV = set_env()
if ENV is None:
    RUNNING_LOCALLY = True
else:
    RUNNING_LOCALLY = False


def set_base_file_path(RUNNING_LOCALLY, ENV):
    if RUNNING_LOCALLY:
        return "../../data/json/corona"
    else:
        if ENV.upper() == 'PROD':
            return "/home/Azafar98/prod/coronavirus-webapp"
        elif ENV.upper() == 'DEV':
            return "/home/Azafar98/dev/coronavirus-webapp"
        else:
            raise ValueError("Invalid environment type. Must be 'DEV' or 'PROD'.")


project_home = set_base_file_path(RUNNING_LOCALLY, ENV)


def _download_corona_data():
    """
    If not downloaded, call the function in download_corona_data.py
    :return:
    """
    import sys
    if project_home not in sys.path:
        sys.path = [project_home] + sys.path

    from src.main.download_corona_data import _run

    download = _run()
    return download


def get_corona_data():
    """
    Get the data to use for analysis. If it is not saved locally, download it
    :return:
    """
    if RUNNING_LOCALLY:
        file_path = project_home + '/{}'
    else:
        file_path = project_home + '/data/json/corona/{}'

    if not (os.path.exists(file_path.format("confirmed_cases.txt"))) or not \
        (os.path.exists(file_path.format("deaths_cases.txt"))) or not \
        (os.path.exists(file_path.format("recovered_cases.txt"))):

        print("corona data not downloaded. Downloading.")

        download = _download_corona_data()

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
    :param str or None country: Country name. Specify None to return all data.
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

    if province.upper() == 'ALL':
        country_data = aggregate_duplicate_countries(country_data)

    elif province is not None:
        provinces = country_data['Province/State'].unique().tolist()
        country_data = country_data.loc[country_data['Province/State'].str.upper() == province.upper(), :]

        # Invalid province specified
        if len(country_data) == 0:
            raise ValueError("Invalid province '{}' specified for country '{}'. Specify province from \n {}."
                             .format(province, country, provinces))
    else:
        if len(country_data) > 1:
            provinces = country_data['Province/State'].unique().tolist()
            warnings.warn("More than one province available for {}. Please specify province from {}, or all will be used."
                          .format(country, provinces))

    country_data = country_data.reset_index(drop=True)
    return country_data


def british_date_format(date):
    return pd.to_datetime(date).strftime("%d/%m/%y")


def get_latest_figures(data, period='TOTAL', pct_change=False):
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

        date = british_date_format(date_cols[-1])

        pct = 0

        # Also return the dates the data is from so we can display this
        return cases, date, pct

    if period.upper() == '24H':
        # Now need to calculate the difference between the two most recent data points
        dates = date_cols[-3:]
        total_df = data.loc[:, dates]

        # New cases in the period is just the difference between the first and last columns since the data is aggregated
        new_cases_df = total_df.iloc[:, -1] - total_df.iloc[:, 1]

        new_cases_sum = new_cases_df.sum(axis=0)

        if pct_change:
            prev_period = total_df.iloc[:, -2] - total_df.iloc[:, 0]
            prev_period_sum = prev_period.sum(axis=0)

            pct = round(((new_cases_sum - prev_period_sum)/prev_period_sum)*100)
        else:
            pct = 0

        date1, date2 = british_date_format(date_cols[-2]), british_date_format(date_cols[-1])

        dates_used = ' - '.join([date1, date2])

        # Also return the dates the data is from so we can display this
        return new_cases_sum, dates_used, pct

    if period.upper() == '7DAYS':
        # Now need to calculate the difference between the two most recent data points
        dates = date_cols[-8:]
        total_df = data.loc[:, dates]

        # New cases in the period is just the difference between the first and last columns since the data is aggregated
        new_cases_df = total_df.iloc[:, -1] - total_df.iloc[:, 1]

        new_cases_sum = new_cases_df.sum(axis=0)

        if pct_change:
            prev_period = total_df.iloc[:, -2] - total_df.iloc[:, 0]
            prev_period_sum = prev_period.sum(axis=0)

            pct = round(((new_cases_sum - prev_period_sum) / prev_period_sum) * 100)
        else:
            pct = 0

        date1, date2 = british_date_format(date_cols[-7]), british_date_format(date_cols[-1])

        dates_used = ' - '.join([date1, date2])

        # Also return the dates the data is from so we can display this
        return new_cases_sum, dates_used, pct


def display_covid_cases(cases=True, period='Total', pct_change=False):
    """

    :param bool cases: If True, return number of cases in period. If False, return dates used for that period.
    :param period: Currently either Total, 24H or 7Days
    :return:
    """

    period = period.upper()

    confirmed, recovered, deaths = get_corona_data()

    # For now, this is set up to use UK data only. Need to figure out Flask a bit better to pass parameters down.
    uk_data = data_for_country(confirmed, 'United Kingdom', province='All')

    if period not in ['TOTAL', '24H', '7DAYS']:
        raise ValueError("Invalid time period. Must be either 'TOTAL', '24H', or '7DAYS'")

    uk_cases, dates, pct = get_latest_figures(uk_data, period=period, pct_change=pct_change)

    if cases is True:
        # return f'{uk_cases:,}'.strip()
        return uk_cases
    elif pct_change is True:
        return pct
    else:
        return str(dates)


def get_covid_time_series(data_type, difference):
    """

    :param data_type:
    :param difference:
    :return:
    """
    if RUNNING_LOCALLY:
        file_path = project_home + '/{}'
    else:
        file_path = project_home + '/data/json/corona/{}'

    data_type = data_type.upper()

    if data_type == 'CONFIRMED':
        if not (os.path.exists(file_path.format("confirmed-covid-time-series.txt")) or
                os.path.exists(file_path.format("confirmed-covid-time-series.txt"))):
            print("data not downloaded. Not downloading.")
            # update_covid_time_series('confirmed')

    elif data_type == 'DEATHS':
        if not (os.path.exists(file_path.format("deaths-covid-time-series.txt")) or
                os.path.exists(file_path.format("deaths-covid-time-series.txt"))):
            print("data not downloaded. Not downloading.")
            # update_covid_time_series('deaths')

    elif data_type == 'RECOVERED':
        if not (os.path.exists(file_path.format("recovered-covid-time-series.txt")) or
                os.path.exists(file_path.format("recovered-covid-time-series.txt"))):
            print("data not downloaded. Not downloading.")
            # update_covid_time_series('recovered')
    else:
        raise ValueError("Invalid data type to get covid time series")

    if difference is True:
        with open(file_path.format("{}-covid-time-series-diff.txt").format(data_type.lower())) as f:
            file = json.load(f)
            # It is easier if this is returned as a string. So read the JSON file, and then dump it again to get into
            # string format AND ensure it's valid JSON.
            str_rep = json.dumps(file)
        return str_rep
    else:
        with open(file_path.format("{}-covid-time-series.txt").format(data_type.lower())) as f:
            file = json.load(f)
            str_rep = json.dumps(file)
        return str_rep


def country_options():

    confirmed, recovered, deaths = get_corona_data()
    # Pass None to get data for all countries back
    country_data = data_for_country(confirmed, None, province='None')

    countries = country_data['Country/Region'].unique().tolist()
    countries = sorted(countries)

    return countries
